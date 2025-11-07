"""
Sistema RAG (Retrieval-Augmented Generation) para el Coach de Bienestar Preventivo.
Utiliza BM25 para búsqueda y OpenAI para generación de planes personalizados.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    print("⚠️ rank-bm25 no instalado. Instalando...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'rank-bm25'])
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️ openai no instalado. Instalando...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'openai'])
    from openai import OpenAI
    HAS_OPENAI = True


@dataclass
class Document:
    """Documento de la base de conocimiento."""
    filename: str
    content: str
    sections: Dict[str, str]  # título -> contenido


class KnowledgeBase:
    """Cargador y gestor de la base de conocimiento local."""
    
    def __init__(self, kb_dir: str = './kb'):
        self.kb_dir = Path(kb_dir)
        self.documents: List[Document] = []
        self.chunks: List[Dict[str, str]] = []
        self._load_documents()
        
    def _load_documents(self):
        """Carga todos los archivos markdown de la base de conocimiento."""
        if not self.kb_dir.exists():
            print(f"⚠️ Directorio {self.kb_dir} no encontrado. Creándolo...")
            self.kb_dir.mkdir(parents=True, exist_ok=True)
            return
        
        md_files = list(self.kb_dir.glob('*.md'))
        if not md_files:
            print(f"⚠️ No se encontraron archivos .md en {self.kb_dir}")
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
            
            # Crear chunks para BM25 (cada sección es un chunk)
            for section_title, section_content in sections.items():
                self.chunks.append({
                    'source': md_file.name,
                    'section': section_title,
                    'content': section_content,
                    'full_text': f"{section_title}\n{section_content}"
                })
        
        print(f"✅ Base de conocimiento cargada: {len(self.documents)} documentos, {len(self.chunks)} chunks")
    
    def _parse_sections(self, markdown_text: str) -> Dict[str, str]:
        """Parsea un documento markdown en secciones."""
        sections = {}
        current_section = "Introducción"
        current_content = []
        
        for line in markdown_text.split('\n'):
            if line.startswith('##'):
                # Guardar sección anterior
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                # Nueva sección
                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Guardar última sección
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
            print("⚠️ No hay chunks disponibles para indexar")
            self.bm25 = None
            return
        
        # Tokenizar chunks para BM25
        tokenized_corpus = [
            self._tokenize(chunk['full_text']) 
            for chunk in self.chunks
        ]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"✅ Índice BM25 creado con {len(self.chunks)} chunks")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenización simple para BM25."""
        # Convertir a minúsculas y separar por espacios/puntuación
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Recupera los top_k chunks más relevantes para la query."""
        if not self.bm25:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Obtener índices de top_k scores
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
            print("⚠️ OPENAI_API_KEY no encontrada. El coach no podrá generar planes.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            print("✅ Cliente OpenAI inicializado")
    
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
            return {
                'plan': self._generate_fallback_plan(user_profile, risk_score, top_drivers),
                'sources': ['diabetes_prevention.md'],
                'error': 'OpenAI API no disponible'
            }
        
        # 1. Construir query para RAG
        if not query:
            driver_names = [d.get('feature', d.get('description', '')) for d in top_drivers[:3]]
            query = f"diabetes prevention lifestyle {' '.join(driver_names)}"
        
        # 2. Recuperar documentos relevantes
        retrieved_docs = self.retriever.retrieve(query, top_k=3)
        
        if not retrieved_docs:
            print("⚠️ No se recuperaron documentos. Usando fallback.")
            return {
                'plan': self._generate_fallback_plan(user_profile, risk_score, top_drivers),
                'sources': [],
                'error': 'No se encontraron documentos relevantes'
            }
        
        # 3. Construir contexto RAG
        context = self._build_context(retrieved_docs)
        sources = list(set([doc['source'] for doc in retrieved_docs]))
        
        # 4. Construir prompt para OpenAI
        prompt = self._build_prompt(user_profile, risk_score, top_drivers, context)
        
        # 5. Generar plan con OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Más económico que gpt-4o
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
                'retrieved_docs': retrieved_docs  # Para debugging
            }
        
        except Exception as e:
            print(f"❌ Error generando plan con OpenAI: {e}")
            return {
                'plan': self._generate_fallback_plan(user_profile, risk_score, top_drivers),
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
        
        # Extraer info del perfil
        age = user_profile.get('age', 'N/A')
        sex = user_profile.get('sex', 'N/A')
        sex_text = 'masculino' if sex == 'M' else 'femenino' if sex == 'F' else 'N/A'
        
        # Formatear drivers
        drivers_text = "\n".join([
            f"- {d.get('description', d.get('feature', 'N/A'))}: "
            f"valor {d.get('value', 'N/A'):.2f} ({d.get('impact', 'N/A')} el riesgo)"
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
    
    def _generate_fallback_plan(
        self, 
        user_profile: Dict, 
        risk_score: float, 
        top_drivers: List[Dict]
    ) -> str:
        """Plan de fallback cuando OpenAI no está disponible."""
        age = user_profile.get('age', 'N/A')
        
        plan = f"""# Plan Personalizado de Bienestar Preventivo

## Tu Perfil
- Edad: {age} años
- Riesgo estimado: {risk_score:.1%}

## Factores a Trabajar
"""
        for i, driver in enumerate(top_drivers[:3], 1):
            plan += f"{i}. {driver.get('description', 'Factor de riesgo')}\n"
        
        plan += """
## Plan de 2 Semanas

### Semana 1: Establece la Base
- **Nutrición**: Incrementa consumo de verduras (2 porciones extra/día)
- **Actividad**: Camina 20 minutos diarios
- **Sueño**: Mantén horario regular (7-8 horas)

### Semana 2: Profundiza
- **Nutrición**: Reduce azúcares refinados (1 cambio diario)
- **Actividad**: Incrementa a 30 minutos + 2 días de fuerza
- **Sueño**: Optimiza higiene del sueño (sin pantallas 1h antes)

## Seguimiento
Monitorea tu progreso semanalmente y ajusta según sea necesario.

⚠️ **IMPORTANTE**: Este plan NO es un diagnóstico médico. Consulta con un profesional de salud.

_Fuentes: Diabetes Prevention Program, American Diabetes Association Guidelines_
"""
        return plan


# Clase de conveniencia para inicializar todo el sistema
class RAGCoachSystem:
    """Sistema completo RAG + Coach."""
    
    def __init__(self, kb_dir: str = './kb', api_key: Optional[str] = None):
        print("🚀 Inicializando sistema RAG Coach...")
        self.kb = KnowledgeBase(kb_dir)
        self.retriever = RAGRetriever(self.kb)
        self.coach = CoachGenerator(self.retriever, api_key)
        print("✅ Sistema RAG Coach listo")
    
    def generate_plan(self, user_profile: Dict, risk_score: float, top_drivers: List[Dict]) -> Dict:
        """Método de conveniencia para generar plan."""
        return self.coach.generate_plan(user_profile, risk_score, top_drivers)


# Test básico
if __name__ == "__main__":
    print("🧪 Test del sistema RAG Coach\n")
    
    # Inicializar sistema
    rag_system = RAGCoachSystem(kb_dir='./kb')
    
    # Perfil de prueba
    test_profile = {
        'age': 45,
        'sex': 'M',
        'height_cm': 175,
        'weight_kg': 95,
        'waist_cm': 105
    }
    
    test_drivers = [
        {'description': 'IMC elevado', 'value': 31.0, 'impact': 'aumenta'},
        {'description': 'Obesidad central', 'value': 1.0, 'impact': 'aumenta'},
        {'description': 'Sedentarismo', 'value': 1.0, 'impact': 'aumenta'}
    ]
    
    # Generar plan
    result = rag_system.generate_plan(
        user_profile=test_profile,
        risk_score=0.65,
        top_drivers=test_drivers
    )
    
    print("\n" + "="*80)
    print("PLAN GENERADO:")
    print("="*80)
    print(result['plan'])
    print("\n" + "="*80)
    print(f"FUENTES: {', '.join(result['sources'])}")
    print("="*80)


