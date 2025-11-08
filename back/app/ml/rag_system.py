import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
import logging

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'rank-bm25'])
    from rank_bm25 import BM25Okapi

try:
    from openai import OpenAI
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'openai'])
    from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Documento de la base de conocimiento."""
    filename: str
    content: str
    sections: Dict[str, str]

class KnowledgeBase:
    """Cargador y gestor de la base de conocimiento local."""
    
    def __init__(self, kb_dir: str):
        self.kb_dir = Path(kb_dir)
        self.documents: List[Document] = []
        self.chunks: List[Dict[str, str]] = []
        self._load_documents()
        
    def _load_documents(self):
        """Carga todos los archivos markdown de la base de conocimiento."""
        if not self.kb_dir.exists():
            logger.warning(f"Directorio {self.kb_dir} no encontrado. Creándolo...")
            self.kb_dir.mkdir(parents=True, exist_ok=True)
            return
        
        md_files = list(self.kb_dir.glob('*.md'))
        if not md_files:
            logger.warning(f"No se encontraron archivos .md en {self.kb_dir}")
            return
        
        for md_file in md_files:
            content = md_file.read_text(encoding='utf-8')
            sections = self._parse_sections(content)
            
            doc = Document(
                filename=md_file.name,
                content=content,
                sections=sections
            )
            self.documents.append(doc)
            
            for section_title, section_content in sections.items():
                self.chunks.append({
                    'source': md_file.name,
                    'section': section_title,
                    'content': section_content,
                    'full_text': f"{section_title}\n{section_content}"
                })
        
        logger.info(f"Base de conocimiento cargada: {len(self.documents)} documentos, {len(self.chunks)} chunks")
    
    def _parse_sections(self, markdown_text: str) -> Dict[str, str]:
        """Parsea un documento markdown en secciones."""
        sections = {}
        current_section = "Introducción"
        current_content = []
        
        for line in markdown_text.split('\n'):
            if line.startswith('##'):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def get_all_chunks(self) -> List[Dict[str, str]]:
        """Retorna todos los chunks de texto."""
        return self.chunks

class RAGRetriever:
    """Recuperador de documentos usando BM25."""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.chunks = self.kb.get_all_chunks()
        
        if not self.chunks:
            logger.warning("No hay chunks disponibles para indexar")
            self.bm25 = None
            return
        
        tokenized_corpus = [
            self._tokenize(chunk['full_text']) 
            for chunk in self.chunks
        ]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"Índice BM25 creado con {len(self.chunks)} chunks")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenización simple para BM25."""
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Recupera los top_k chunks más relevantes para la query."""
        if not self.bm25:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        top_indices = sorted(
            range(len(scores)), 
            key=lambda i: scores[i], 
            reverse=True
        )[:top_k]
        
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx].copy()
            chunk['score'] = float(scores[idx])
            results.append(chunk)
        
        return results

class CoachGenerator:
    """Generador de planes personalizados usando OpenAI + RAG."""
    
    def __init__(self, retriever: RAGRetriever, api_key: Optional[str] = None):
        self.retriever = retriever
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no encontrada. El coach no podrá generar planes.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("Cliente OpenAI inicializado")
    
    def generate_plan(
        self, 
        user_profile: Dict,
        risk_score: float,
        top_drivers: List[Dict],
        query: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Genera un plan personalizado de 2 semanas usando RAG.
        
        Args:
            user_profile: Perfil del usuario (edad, sexo, métricas)
            risk_score: Puntaje de riesgo (0-1)
            top_drivers: Lista de factores que impulsan el riesgo
            query: Query opcional para búsqueda RAG
        
        Returns:
            Dict con 'plan' (texto) y 'sources' (lista de fuentes)
        """
        if not self.client:
            message = self._service_unavailable_message()
            return {
                'plan': message,
                'sources': [],
                'error': 'OpenAI API no disponible'
            }
        
        if not query:
            driver_names = [d.get('feature', d.get('description', '')) for d in top_drivers[:3]]
            query = f"diabetes prevention lifestyle {' '.join(driver_names)}"
        
        retrieved_docs = self.retriever.retrieve(query, top_k=3)
        
        if not retrieved_docs:
            logger.error("No se recuperaron documentos de la base de conocimiento.")
            raise Exception("No se encontraron documentos relevantes en la base de conocimiento. Por favor, verifica la configuración de la KB.")
        
        context = self._build_context(retrieved_docs)
        sources = list(set([doc['source'] for doc in retrieved_docs]))
        
        prompt = self._build_prompt(user_profile, risk_score, top_drivers, context)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un asistente de salud preventiva especializado en diabetes y riesgo cardiometabólico. "
                            "Tu rol es generar planes SMART (específicos, medibles, alcanzables, relevantes, temporales) "
                            "de 2 semanas basándote ÚNICAMENTE en la información proporcionada. "
                            "NUNCA inventes información médica. SIEMPRE cita las fuentes proporcionadas. "
                            "Usa lenguaje claro, inclusivo y no-diagnóstico. "
                            "INCLUYE un disclaimer explícito de que NO es diagnóstico médico."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            plan_text = response.choices[0].message.content.strip()
            
            return {
                'plan': plan_text,
                'sources': sources,
                'retrieved_docs': retrieved_docs
            }
        
        except Exception as e:
            logger.error(f"Error generando plan con OpenAI: {e}")
            message = self._service_unavailable_message()
            return {
                'plan': message,
                'sources': sources,
                'error': str(e)
            }
    
    def _build_context(self, retrieved_docs: List[Dict]) -> str:
        """Construye el contexto RAG a partir de documentos recuperados."""
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(
                f"[FUENTE {i}: {doc['source']} - {doc['section']}]\n"
                f"{doc['content']}\n"
            )
        return "\n".join(context_parts)
    
    def _build_prompt(
        self, 
        user_profile: Dict, 
        risk_score: float, 
        top_drivers: List[Dict], 
        context: str
    ) -> str:
        """Construye el prompt para OpenAI."""
        
        age = user_profile.get('age') or user_profile.get('edad')
        if age is None:
            raise ValueError("La edad del usuario es requerida")
        
        sex = user_profile.get('sex') or user_profile.get('genero')
        if sex not in ['M', 'F']:
            raise ValueError("El sexo del usuario debe ser 'M' o 'F'")
        
        sex_text = 'masculino' if sex == 'M' else 'femenino'
        
        drivers_text = "\n".join([
            f"- {d.get('description') or d.get('feature', 'Factor desconocido')}: "
            f"valor {d.get('value', 0):.2f} ({d.get('impact', 'impacto desconocido')} el riesgo)"
            for d in top_drivers[:5]
        ])
        
        prompt = f"""Genera un plan personalizado de bienestar preventivo de 2 semanas para esta persona.

**PERFIL DEL USUARIO:**
- Edad: {age} años
- Sexo: {sex_text}
- Puntaje de riesgo cardiometabólico: {risk_score:.1%}

**FACTORES DE RIESGO PRINCIPALES (según modelo ML):**
{drivers_text}

**INFORMACIÓN BASADA EN EVIDENCIA (debes citar estas fuentes):**
{context}

**INSTRUCCIONES:**
1. Crea un plan de 2 semanas con acciones SMART (específicas, medibles, alcanzables, relevantes, temporales)
2. Prioriza los factores de riesgo identificados (especialmente los primeros 3)
3. Organiza el plan por áreas: nutrición, actividad física, sueño, manejo de estrés
4. Incluye metas semanales concretas
5. CITA explícitamente las fuentes proporcionadas arriba (ej: "según [FUENTE 1]...")
6. Usa lenguaje claro, accesible e inclusivo
7. INCLUYE AL FINAL un disclaimer: "⚠️ IMPORTANTE: Este plan NO es un diagnóstico médico. Consulta con un profesional de salud antes de iniciar cambios significativos."

Genera el plan ahora:"""
        
        return prompt
    
    def _service_unavailable_message(self) -> str:
        """Mensaje estándar cuando el servicio no está disponible."""
        return (
            "El servicio de generación de planes personalizados no está disponible en este momento. "
            "Por favor, inténtalo nuevamente más tarde."
        )

class RAGCoachSystem:
    """Sistema completo RAG + Coach."""
    
    def __init__(self, kb_dir: str, api_key: Optional[str] = None):
        logger.info("Inicializando sistema RAG Coach...")
        self.kb = KnowledgeBase(kb_dir)
        self.retriever = RAGRetriever(self.kb)
        self.coach = CoachGenerator(self.retriever, api_key)
        logger.info("Sistema RAG Coach listo")
    
    def generate_plan(self, user_profile: Dict, risk_score: float, top_drivers: List[Dict]) -> Dict:
        """Método de conveniencia para generar plan."""
        return self.coach.generate_plan(user_profile, risk_score, top_drivers)

