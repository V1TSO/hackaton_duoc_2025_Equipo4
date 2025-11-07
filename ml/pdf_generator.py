"""
Generador de PDFs para el plan personalizado de bienestar.
Utiliza reportlab para crear PDFs con formato profesional.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO
from typing import Dict, List
import textwrap


class WellnessPlanPDF:
    """Generador de PDF para planes de bienestar personalizados."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Disclaimer
        self.styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#E74C3C'),
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=20,
            rightIndent=20,
            borderColor=colors.HexColor('#E74C3C'),
            borderWidth=1,
            borderPadding=10,
            alignment=TA_JUSTIFY,
            fontName='Helvetica-Bold'
        ))
        
        # Información destacada
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
    
    def generate_pdf(
        self,
        user_profile: Dict,
        risk_score: float,
        risk_level: str,
        drivers: List[Dict],
        plan_text: str,
        sources: List[str]
    ) -> BytesIO:
        """
        Genera un PDF con el plan personalizado.
        
        Args:
            user_profile: Perfil del usuario
            risk_score: Puntaje de riesgo (0-1)
            risk_level: Nivel de riesgo (Bajo/Moderado/Alto)
            drivers: Lista de factores que impulsan el riesgo
            plan_text: Texto del plan generado
            sources: Lista de fuentes citadas
        
        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Contenedor de elementos
        story = []
        
        # 1. Título
        story.append(Paragraph(
            "🏥 Plan Personalizado de Bienestar Preventivo",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # 2. Fecha de generación
        fecha = datetime.now().strftime("%d de %B de %Y")
        story.append(Paragraph(
            f"<i>Generado el {fecha}</i>",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Perfil del usuario
        story.append(Paragraph("Tu Perfil", self.styles['CustomHeading']))
        
        age = user_profile.get('age', 'N/A')
        sex = user_profile.get('sex', 'N/A')
        sex_text = 'Masculino' if sex == 'M' else 'Femenino' if sex == 'F' else 'N/A'
        height = user_profile.get('height_cm', 'N/A')
        weight = user_profile.get('weight_kg', 'N/A')
        
        # Calcular IMC si hay datos
        bmi = 'N/A'
        if isinstance(height, (int, float)) and isinstance(weight, (int, float)):
            bmi_val = weight / ((height / 100) ** 2)
            bmi = f"{bmi_val:.1f}"
        
        profile_data = [
            ['Edad', f'{age} años'],
            ['Sexo', sex_text],
            ['Altura', f'{height} cm' if height != 'N/A' else 'N/A'],
            ['Peso', f'{weight} kg' if weight != 'N/A' else 'N/A'],
            ['IMC', bmi]
        ]
        
        profile_table = Table(profile_data, colWidths=[2*inch, 3*inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(profile_table)
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Evaluación de Riesgo
        story.append(Paragraph("Evaluación de Riesgo", self.styles['CustomHeading']))
        
        risk_color = colors.green if risk_score < 0.3 else colors.orange if risk_score < 0.6 else colors.red
        
        risk_data = [
            ['Puntaje de Riesgo', f'{risk_score:.1%}'],
            ['Nivel de Riesgo', risk_level]
        ]
        
        risk_table = Table(risk_data, colWidths=[2*inch, 3*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
            ('BACKGROUND', (1, 1), (1, 1), risk_color.clone(alpha=0.3)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))
        
        # 5. Factores de Riesgo Principales
        story.append(Paragraph("Factores que Impulsan tu Riesgo", self.styles['CustomHeading']))
        
        for i, driver in enumerate(drivers[:5], 1):
            desc = driver.get('description', 'Factor de riesgo')
            value = driver.get('value', 'N/A')
            impact = driver.get('impact', 'afecta')
            
            if isinstance(value, (int, float)):
                value_str = f"{value:.2f}"
            else:
                value_str = str(value)
            
            story.append(Paragraph(
                f"{i}. <b>{desc}</b>: valor {value_str} ({impact} el riesgo)",
                self.styles['CustomBody']
            ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # 6. Plan Personalizado
        story.append(Paragraph("Tu Plan de Bienestar de 2 Semanas", self.styles['CustomHeading']))
        
        # Procesar el plan (dividir en párrafos y formatear)
        plan_paragraphs = plan_text.split('\n\n')
        for para in plan_paragraphs:
            if para.strip():
                # Detectar encabezados (líneas que empiezan con #)
                if para.strip().startswith('##'):
                    heading_text = para.strip().replace('##', '').strip()
                    story.append(Paragraph(heading_text, self.styles['CustomHeading']))
                elif para.strip().startswith('#'):
                    heading_text = para.strip().replace('#', '').strip()
                    story.append(Paragraph(heading_text, self.styles['CustomHeading']))
                else:
                    # Reemplazar markdown básico
                    para = para.replace('**', '<b>').replace('**', '</b>')
                    para = para.replace('*', '<i>').replace('*', '</i>')
                    story.append(Paragraph(para, self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # 7. Fuentes
        if sources:
            story.append(Paragraph("Fuentes Consultadas", self.styles['CustomHeading']))
            sources_text = ", ".join(sources)
            story.append(Paragraph(
                f"<i>{sources_text}</i>",
                self.styles['CustomBody']
            ))
            story.append(Spacer(1, 0.3*inch))
        
        # 8. Disclaimer (al final, destacado)
        disclaimer_text = (
            "⚠️ <b>IMPORTANTE - DISCLAIMER MÉDICO:</b> "
            "Este plan NO constituye un diagnóstico médico ni reemplaza la consulta con profesionales "
            "de salud certificados. Las recomendaciones son de naturaleza preventiva y educativa. "
            "Consulta con tu médico antes de realizar cambios significativos en tu dieta, actividad "
            "física o estilo de vida, especialmente si tienes condiciones médicas preexistentes."
        )
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(disclaimer_text, self.styles['Disclaimer']))
        
        # Pie de página
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "<i>Generado por el Coach de Bienestar Preventivo - Hackathon IA Duoc UC 2025</i>",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))
        
        # Construir el PDF
        doc.build(story)
        
        # Retornar el buffer
        buffer.seek(0)
        return buffer


# Función de conveniencia
def generate_wellness_pdf(
    user_profile: Dict,
    risk_score: float,
    risk_level: str,
    drivers: List[Dict],
    plan_text: str,
    sources: List[str]
) -> BytesIO:
    """
    Función de conveniencia para generar un PDF de plan de bienestar.
    
    Returns:
        BytesIO con el contenido del PDF listo para descarga
    """
    generator = WellnessPlanPDF()
    return generator.generate_pdf(
        user_profile=user_profile,
        risk_score=risk_score,
        risk_level=risk_level,
        drivers=drivers,
        plan_text=plan_text,
        sources=sources
    )


# Test
if __name__ == "__main__":
    print("🧪 Test del generador de PDF")
    
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
    
    test_plan = """# Plan Personalizado

## Semana 1
- Incrementa consumo de verduras
- Camina 20 minutos diarios

## Semana 2
- Reduce azúcares refinados
- Incrementa actividad física

⚠️ Este plan NO es un diagnóstico médico."""
    
    pdf_buffer = generate_wellness_pdf(
        user_profile=test_profile,
        risk_score=0.65,
        risk_level="Alto",
        drivers=test_drivers,
        plan_text=test_plan,
        sources=["diabetes_prevention.md"]
    )
    
    # Guardar test
    with open('test_plan.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("✅ PDF generado: test_plan.pdf")


