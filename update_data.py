import pandas as pd
import json
import os

def process_excel(file_path, output_json='data.json'):
    print(f"Lendo planilha: {file_path}...")
    
    try:
        df = pd.read_excel(file_path, sheet_name='Worksheet')
        
        # --- 1. TRATAMENTO DE DATAS (AGENDAMENTO) ---
        col_agendamento = 'Agendamento (horário de Brasília)'
        df[col_agendamento] = pd.to_datetime(df[col_agendamento], errors='coerce')
        
        def get_turno(dt):
            if pd.isna(dt): return "Não Informado"
            hour = dt.hour
            # CORREÇÃO TURNO: Lógica robusta para os 3 turnos
            if 5 <= hour < 12: return "Matutino"
            elif 12 <= hour < 18: return "Vespertino"
            else: return "Noturno" # Abrange das 18h às 04h

        def get_mes(dt):
            if pd.isna(dt): return "Não Informado"
            meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            return meses[dt.month - 1]

        df['_turno'] = df[col_agendamento].apply(get_turno)
        df['_mes'] = df[col_agendamento].apply(get_mes)
        
        # --- 2. SEPARAÇÃO DE MÉTRICAS ---
        df['_provas_aplicadas'] = pd.to_numeric(df['Status de Geração'], errors='coerce').fillna(0).astype(int)
        df['_provas_nao_aplicadas'] = pd.to_numeric(df['Provas Aptas'], errors='coerce').fillna(0).astype(int)
        df['_tabulacao_feita'] = pd.to_numeric(df['Tabulação Feita'], errors='coerce').fillna(0).astype(int)
        df['_tabulacao_pendente'] = pd.to_numeric(df['Tabulação Pendente'], errors='coerce').fillna(0).astype(int)
        df['_total_provas_geradas'] = pd.to_numeric(
        df['Total de Provas Geradas'],
            errors='coerce'
        ).fillna(0).astype(int)
        df['_total_alunos'] = pd.to_numeric(
        df['Alunos Homologados'],
            errors='coerce'
        ).fillna(0).astype(int)

        df['_prova_objetiva'] = pd.to_numeric(
            df['Prova Objetiva'],
            errors='coerce'
        ).fillna(0).astype(int)

        # --- 3. LIMPEZA E EXPORTAÇÃO ---
        df[col_agendamento] = df[col_agendamento].dt.strftime('%d/%m/%Y %H:%M').fillna('Não Informado')
        
        cols_to_keep = [
            'Unidade operacional (Escola)',
            'Curso',
            'Modalidade',
            'Turma',
            col_agendamento,
            '_turno',
            '_mes',
            '_total_provas_geradas',
            '_provas_aplicadas',
            '_provas_nao_aplicadas',
            '_tabulacao_feita',
            '_tabulacao_pendente',
            '_total_alunos',
            '_prova_objetiva'
        ]
        
        data = df[cols_to_keep].to_dict(orient='records')
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso! {len(data)} registros processados.")
        
    except Exception as e:
        print(f"Erro crítico: {e}")

if __name__ == "__main__":
    FILE = 'PlanilhaAvaliaçãoPratica.xlsx'
    if os.path.exists(FILE):
        process_excel(FILE)
    else:
        print(f"Erro: Arquivo {FILE} não encontrado.")
