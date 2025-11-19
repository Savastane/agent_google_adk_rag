import pdfplumber
import json
import re

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um arquivo PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

def parse_cv_text(text):
    """Analisa o texto extraído do CV e o estrutura em um dicionário."""
    # Esta é uma função de exemplo e pode precisar de ajustes com base na estrutura do seu CV.
    # Tenta extrair informações com base em títulos comuns.
    
    # Exemplo de extração de nome (geralmente no início)
    name_match = re.search(r"^([A-ZÀ-Ú][a-zà-ú]+(?:\s[A-ZÀ-Ú][a-zà-ú]+)+)", text)
    name = name_match.group(1).strip() if name_match else "Nome não encontrado"

    # Exemplo de extração de seções (Experiência, Educação, etc.)
    experience = re.search(r"Experiência Profissional\n(.*?)(?:Formação Acadêmica|Habilidades|Idiomas|$)", text, re.DOTALL | re.IGNORECASE)
    education = re.search(r"Formação Acadêmica\n(.*?)(?:Experiência Profissional|Habilidades|Idiomas|$)", text, re.DOTALL | re.IGNORECASE)
    skills = re.search(r"Habilidades\n(.*?)(?:Experiência Profissional|Formação Acadêmica|Idiomas|$)", text, re.DOTALL | re.IGNORECASE)

    cv_data = {
        "name": name,
        "experience": experience.group(1).strip() if experience else "",
        "education": education.group(1).strip() if education else "",
        "skills": skills.group(1).strip() if skills else ""
    }
    return cv_data

def create_json_structure(cv_data):
    """Cria a estrutura JSON final com documentos e um grafo."""
    documents = []
    nodes = []
    relationships = []

    # Nó principal para a pessoa
    person_id = cv_data['name'].replace(' ', '_')
    nodes.append({"id": person_id, "label": "Pessoa", "properties": {"name": cv_data['name']}})
    documents.append({"id": "person_summary", "subject": cv_data['name'], "content": f"{cv_data['name']} é um profissional com experiência e formação descritas em seu currículo."})

    # Processar Educação
    if cv_data['education']:
        doc_id = f"edu_{person_id}"
        documents.append({"id": doc_id, "subject": "Educação", "content": cv_data['education']})
        # Simplificação: adiciona uma instituição genérica. A lógica real seria mais complexa.
        school_name = "Instituição de Ensino"
        school_id = school_name.replace(' ', '_')
        if not any(n['id'] == school_id for n in nodes):
            nodes.append({"id": school_id, "label": "Instituicao", "properties": {"name": school_name}})
        relationships.append({"source": person_id, "target": school_id, "type": "ESTUDOU_EM"})

    # Processar Experiência
    if cv_data['experience']:
        doc_id = f"exp_{person_id}"
        documents.append({"id": doc_id, "subject": "Experiência", "content": cv_data['experience']})
        # Simplificação: adiciona uma empresa genérica.
        company_name = "Empresa"
        company_id = company_name.replace(' ', '_')
        if not any(n['id'] == company_id for n in nodes):
            nodes.append({"id": company_id, "label": "Empresa", "properties": {"name": company_name}})
        relationships.append({"source": person_id, "target": company_id, "type": "TRABALHOU_EM"})

    # Processar Habilidades
    if cv_data['skills']:
        doc_id = f"skills_{person_id}"
        documents.append({"id": doc_id, "subject": "Habilidades", "content": cv_data['skills']})
        # Simplificação: adiciona habilidades como nós individuais.
        for skill in cv_data['skills'].split('\n'):
            skill = skill.strip()
            if skill:
                skill_id = skill.replace(' ', '_')
                if not any(n['id'] == skill_id for n in nodes):
                    nodes.append({"id": skill_id, "label": "Habilidade", "properties": {"name": skill}})
                relationships.append({"source": person_id, "target": skill_id, "type": "POSSUI_HABILIDADE"})

    return {
        "documents": documents,
        "graph": {
            "nodes": nodes,
            "relationships": relationships
        }
    }

def main():
    """Função principal para processar o CV e gerar o JSON."""
    pdf_path = 'data/CV.pdf'
    json_path = 'data/cv.json'

    print(f"Extraindo texto de {pdf_path}...")
    cv_text = extract_text_from_pdf(pdf_path)
    
    print("Analisando o texto do CV...")
    parsed_data = parse_cv_text(cv_text)
    
    print("Criando a estrutura JSON...")
    json_data = create_json_structure(parsed_data)

    print(f"Salvando o resultado em {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
