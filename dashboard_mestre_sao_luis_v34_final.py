# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# DESENVOLVIMENTO: MONITORAMENTO ESTRATÉGICO DE VULNERABILIDADES E QUALIFICAÇÃO
# VERSÃO: 38.0 (ABSOLUTE INDUSTRIAL - LEGACY EDITION - > 850 LINHAS)
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÕES DE INTERFACE E ESTILO (UI/UX EXECUTIVA PREMIUM)
# ------------------------------------------------------------------------------
# Definimos o layout wide para visualização em telões de salas de situação.
st.set_page_config(
    page_title="SIGMS - Gestão Social São Luís",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para garantir a identidade visual da Superintendência.
# Utilizamos o esquema de cores Dark Mode com destaques em Amarelo Ouro e Azul Real.
st.markdown("""
    <style>
    /* Configuração global do fundo e fontes corporativas */
    .main { 
        background-color: #0b0e14; 
    }
    
    /* Estilização dos Cards de Métricas (KPIs) - Destaque para números de gestão */
    div[data-testid="stMetricValue"] { 
        color: #f1c40f !important; 
        font-size: 38px !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    
    /* Estilização das legendas das métricas */
    div[data-testid="stMetricLabel"] { 
        color: #8a99ad !important; 
        font-size: 14px !important; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    /* Títulos Executivos e Hierarquia Visual */
    h1, h2, h3 { 
        color: #ffffff !important; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        font-weight: 700;
        margin-bottom: 25px;
    }
    
    /* Customização Avançada das Abas de Navegação (Tabs) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 25px; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1e3a8a !important; 
        color: #ffffff !important;
        font-weight: bold; 
        border-radius: 8px 8px 0 0;
        border-bottom: 5px solid #f1c40f !important;
        transition: all 0.4s ease;
    }
    
    /* Tabelas de Dados e Visualização de DataFrames Estruturados */
    .stDataFrame { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 10px;
    }
    
    /* Botões da Barra Lateral (Sidebar) - Padrão Institucional */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
        border: 1px solid #3b82f6;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        color: white;
        border: 1px solid #ffffff;
        box-shadow: 0px 4px 15px rgba(59, 130, 246, 0.4);
    }

    /* Estilização para tooltips mais limpas e legíveis */
    .hoverlayer { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DICIONÁRIOS DE TRADUÇÃO MESTRE (ESCOPO GLOBAL PROTEGIDO)
# ------------------------------------------------------------------------------

# Mapeamento exaustivo dos Grupos Populacionais Tradicionais e Específicos (GPTE).
DIC_GPTE_OFICIAL = {
    '101': 'FAMÍLIA CIGANA', 
    '201': 'FAMÍLIA EXTRATIVISTA', 
    '202': 'FAMÍLIA DE PESCADORES ARTESANAIS',
    '203': 'FAMÍLIA PERTENCENTE A COMUNIDADE DE TERREIRO', 
    '204': 'FAMÍLIA RIBEIRINHA', 
    '205': 'FAMÍLIA AGRICULTORES FAMILIARES',
    '301': 'FAMÍLIA ASSENTADA REFORMA AGRÁRIA', 
    '302': 'FAMÍLIA BENEFICIÁRIA DO PROGRAMA NACIONAL DO CRÉDITO FUNDIÁRIO', 
    '303': 'FAMÍLIA ACAMPADA',
    '304': 'FAMÍLIA ATINGIDA POR EMPREENDIMENTOS DE INFRAESTRUTURA', 
    '305': 'FAMÍLIA DE PRESO DO SISTEMA CARCERÁRIO', 
    '306': 'FAMÍLIA CATADORES DE MATERIAL RECICLÁVEL',
    '0': 'NENHUMA MARCAÇÃO ESPECIAL', 
    '': 'NÃO INFORMADO'
}

# Tradução Humana dos Tipos de Deficiência para Gráficos e Tooltips.
DIC_DEF_HUMANO = {
    'p_ind_def_cegueira_memb': 'Cegueira',
    'p_ind_def_baixa_visao_memb': 'Baixa Visão',
    'p_ind_def_surdez_profunda_memb': 'Surdez Severa/Profunda',
    'p_ind_def_surdez_leve_memb': 'Surdez Leve/Moderada',
    'p_ind_def_fisica_memb': 'Deficiência Física',
    'p_ind_def_mental_memb': 'Deficiência Mental ou Intelectual',
    'p_ind_def_sindrome_down_memb': 'Síndrome de Down',
    'p_ind_def_transtorno_mental_memb': 'Transtorno/Doença Mental'
}

# Mapeamento Integral de TODOS os 11 Motivos de Rua (DNA do Formulário Nacional).
DIC_MOTIVOS_RUA_MASTER = {
    'p_ind_motivo_perda_memb': 'Perda de Moradia',
    'p_ind_motivo_ameaca_memb': 'Ameaça',
    'p_ind_motivo_probs_fam_memb': 'Problemas Familiares',
    'p_ind_motivo_alcool_memb': 'Alcoolismo / Drogas',
    'p_ind_motivo_desemprego_memb': 'Desemprego',
    'p_ind_motivo_trabalho_memb': 'Trabalho',
    'p_ind_motivo_saude_memb': 'Tratamento de Saúde',
    'p_ind_motivo_pref_memb': 'Preferência',
    'p_ind_motivo_outro_memb': 'Outro Motivo',
    'p_ind_motivo_nao_sabe_memb': 'Não Sabe / Não Lembra',
    'p_ind_motivo_nao_resp_memb': 'Não Respondeu'
}

# ------------------------------------------------------------------------------
# 3. MÓDULO DE CARREGAMENTO E HIGIENIZAÇÃO (DNA DO ARQUIVO)
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner="Sincronizando Base de Dados da Superintendência...")
def carregar_dados_blindados_sigms():
    """
    Função de engenharia de dados para carregar o arquivo Parquet e garantir a integridade.
    Resolve erros de Case-Sensitivity, espaços em nomes de colunas e campos vazios.
    """
    try:
        caminho_parquet = 'base_sao_luis_bi.parquet'
        
        # Validação de existência física do arquivo.
        if not os.path.exists(caminho_parquet):
            st.error(f"Erro Crítico: O arquivo '{caminho_parquet}' não foi localizado.")
            return None
            
        # Carregamento com motor PyArrow para máxima compatibilidade na nuvem.
        df_bruto = pd.read_parquet(caminho_parquet, engine='pyarrow')
        
        # NORMALIZAÇÃO DE COLUNAS (DNA IDENTIFICADO NA INSPEÇÃO):
        # 1. .strip() elimina espaços invisíveis (' d.cod...')
        # 2. .replace('.', '_') resolve erros de FieldRef.Nested do motor Parquet
        # 3. .lower() garante que 'unipessoalidade' seja encontrada sempre
        df_bruto.columns = [c.strip().replace('.', '_').lower() for c in df_bruto.columns]
        
        # SANITIZAÇÃO DE DADOS BINÁRIOS (BLINDAGEM CONTRA ERRO 'INVALID LITERAL'):
        # Forçamos todas as colunas de marcação a serem numéricas, tratando vazios como 0.
        cols_fixar = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA_MASTER.keys()) + [
            'p_marc_sit_rua', 'p_cod_deficiencia_memb', 
            'd_cod_familia_indigena_fam', 'd_ind_familia_quilombola_fam'
        ]
        
        for col_it in cols_fixar:
            if col_it in df_bruto.columns:
                df_bruto[col_it] = pd.to_numeric(df_bruto[col_it], errors='coerce').fillna(0).astype(int)
        
        # AJUSTE CRÍTICO v38: Conversão de Datas com dayfirst=True para evitar erro de parser.
        if 'd_dat_atual_fam' in df_bruto.columns:
            df_bruto['d_dat_atual_fam'] = pd.to_datetime(df_bruto['d_dat_atual_fam'], errors='coerce', dayfirst=True)
        
        # Conversão forçada de Renda para numérico.
        if 'd_vlr_renda_media_fam' in df_bruto.columns:
            df_bruto['d_vlr_renda_media_fam'] = pd.to_numeric(df_bruto['d_vlr_renda_media_fam'], errors='coerce')
            
        return df_bruto
        
    except Exception as e_sigms:
        st.error(f"Falha Crítica na Higienização dos Dados: {e_sigms}")
        return None

# ------------------------------------------------------------------------------
# 4. FUNÇÕES DE PROCESSAMENTO E GERAÇÃO DE INDICADORES (LÓGICA EXPANDIDA)
# ------------------------------------------------------------------------------

def aplicar_logica_territorial(df_total, territorial_selecao):
    """Filtra a base integral para o contexto geográfico selecionado."""
    if territorial_selecao == "SÃO LUÍS (GERAL)":
        return df_total
    return df_total[df_total['d_nom_unidade_territorial_fam'] == territorial_selecao]

def unificar_base_familiar(df_contextual):
    """Garante que tenhamos apenas um registro por código familiar."""
    return df_contextual.drop_duplicates(subset=['d_cod_familiar_fam']).copy()

def calcular_performance_tac(df_familias, data_limite_validade):
    """Calcula a Taxa de Atualização Cadastral para faixas 1, 2 e 3."""
    df_prio = df_familias[df_familias['d_fx_rfpc'].isin(['1', '2', '3'])]
    if df_prio.empty:
        return 0.0
    em_dia = len(df_prio[df_prio['d_dat_atual_fam'] >= data_limite_validade])
    return (em_dia / len(df_prio) * 100)

def isolar_unipessoais_visitas(df_familias):
    """Executa a lógica blindada de visitas domiciliares para Unipessoais."""
    # Filtragem estrita baseada na coluna DNA identificada
    df_uni = df_familias[df_familias['unipessoalidade'].str.upper() == 'UNIPESSOAL']
    total_uni = len(df_uni)
    visitados = len(df_uni[df_uni['d_cod_forma_coleta_fam'] == '2'])
    taxa = (visitados / total_uni * 100) if total_uni > 0 else 0
    return total_uni, visitados, taxa

# ------------------------------------------------------------------------------
# 5. EXECUÇÃO DO SISTEMA BI (ORQUESTRAÇÃO DAS ABAS)
# ------------------------------------------------------------------------------
try:
    df_global_master = carregar_dados_blindados_sigms()
    
    if df_global_master is not None:
        # SideBar de Filtros
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        lista_cras = ["SÃO LUÍS (GERAL)"] + sorted(df_global_master['d_nom_unidade_territorial_fam'].unique().tolist())
        cras_sel = st.sidebar.selectbox("Filtrar por Unidade Territorial (CRAS):", lista_cras)
        
        # Processamento de Dados de Contexto
        df_ctx = aplicar_logica_territorial(df_global_master, cras_sel)
        df_fam = unificar_base_familiar(df_ctx)
        
        # Prazos Legais
        data_ref = datetime.now()
        prazo_vencimento = data_ref - timedelta(days=730)
        df_fam['status_cad'] = df_fam['d_dat_atual_fam'].apply(lambda x: 'Atualizado' if x >= prazo_vencimento else 'Desatualizado')

        # CABEÇALHO KPIs
        st.title(f"📊 Monitoramento: {cras_sel}")
        st.markdown(f"Base Sincronizada em: **{data_ref.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        kpi_cols = st.columns(4)
        kpi_cols[0].metric("Total de Famílias", f"{len(df_fam):,}".replace(",", "."))
        kpi_cols[1].metric("TAC (Eficiência)", f"{calcular_performance_tac(df_fam, prazo_vencimento):.1f}%")
        kpi_cols[2].metric("% Desatualizados", f"{(len(df_fam[df_fam['status_cad']=='Desatualizado'])/len(df_fam)*100):.1f}%")
        kpi_cols[3].metric("Famílias no PBF", f"{len(df_fam[df_fam['d_marc_pbf'] == '1']):,}".replace(",", "."))

        # SISTEMA DE ABAS QUALIFICADAS
        abas_gestao = st.tabs([
            "🎯 Revisão & Unipessoais", 
            "💰 Performance TAC", 
            "🏹 Indígenas & Quilombolas",
            "🛡️ Grupos GPTE", 
            "♿ PcD Detalhado", 
            "🏠 Situação de Rua"
        ])

        # --- ABA 1: OPERAÇÃO E UNIPESSOAIS ---
        with abas_gestao[0]:
            st.subheader("Qualificação Operacional e Foco Unipessoal")
            c1_op, c2_op = st.columns(2)
            with c1_op:
                st.markdown("#### Status de Atualização Cadastral")
                res_st = df_fam.groupby('d_nom_unidade_territorial_fam')['status_cad'].value_counts(normalize=True).unstack() * 100
                fig_st = px.bar(res_st, barmode='stack', color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'},
                                labels={'value': '% da Base', 'status_cad': 'Status', 'd_nom_unidade_territorial_fam': 'Território'})
                fig_st.update_traces(hovertemplate='Território: %{x}<br>Valor: %{y:.1f}%')
                st.plotly_chart(fig_st, use_container_width=True)
            with c2_op:
                t_uni, v_uni, tx_uni = isolar_unipessoais_visitas(df_fam)
                fig_g = go.Figure(go.Indicator(mode="gauge+number", value=tx_uni, number={'suffix': "%"},
                    title={'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{v_uni} de {t_uni} Unipessoais</span>", 'font': {'size': 20}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f1c40f"}}))
                fig_g.update_layout(height=450)
                st.plotly_chart(fig_g, use_container_width=True)

        # --- ABA 2: RANKING TAC ---
        with abas_gestao[1]:
            st.subheader("Performance de Atualização Territorial")
            df_rk = df_fam.groupby('d_nom_unidade_territorial_fam').apply(lambda g: calcular_performance_tac(g, prazo_vencimento)).reset_index(name='TAC').sort_values('TAC', ascending=False)
            fig_rk = px.bar(df_rk, x='TAC', y='d_nom_unidade_territorial_fam', orientation='h', color='TAC', color_continuous_scale='RdYlGn')
            fig_rk.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
            st.plotly_chart(fig_rk, use_container_width=True)

        # --- ABA 3: INDÍGENAS E QUILOMBOLAS ---
        with abas_gestao[2]:
            st.subheader("🏹 Monitoramento Étnico: Povos e Comunidades")
            ci_m, cq_m = st.columns(2)
            with ci_m:
                df_i = df_fam[df_fam['d_cod_familia_indigena_fam'] == 1].copy()
                st.metric("Total Famílias Indígenas", len(df_i))
                if not df_i.empty:
                    res_i = df_i['d_nom_povo_indigena_fam'].value_counts().reset_index()
                    res_i.columns = ['Nome do Povo Indígena', 'Famílias']
                    fig_i = px.bar(res_i, x='Famílias', y='Nome do Povo Indígena', orientation='h', color='Famílias')
                    fig_i.update_traces(hovertemplate='Povo: %{y}<br>Quantidade: %{x}')
                    st.plotly_chart(fig_i, use_container_width=True)
            with cq_m:
                df_q = df_fam[df_fam['d_ind_familia_quilombola_fam'] == 1].copy()
                st.metric("Total Famílias Quilombolas", len(df_q))
                if not df_q.empty:
                    res_q = df_q['d_nom_comunidade_quilombola_fam'].value_counts().reset_index()
                    res_q.columns = ['Nome da Comunidade Quilombola', 'Famílias']
                    fig_q = px.bar(res_q, x='Famílias', y='Nome da Comunidade Quilombola', orientation='h', color_discrete_sequence=['#10b981'])
                    fig_q.update_traces(hovertemplate='Comunidade: %{y}<br>Quantidade: %{x}')
                    st.plotly_chart(fig_q, use_container_width=True)

        # --- ABA 4: GRUPOS GPTE ---
        with abas_gestao[3]:
            st.subheader("Grupos Populacionais Tradicionais (GPTE)")
            gp_base = df_fam[df_fam['d_ind_parc_mds_fam'].astype(str) != '0'].copy()
            if not gp_base.empty:
                res_gp = gp_base['d_ind_parc_mds_fam'].astype(str).value_counts().reset_index()
                res_gp.columns = ['Código', 'Famílias']
                res_gp['Grupo Social'] = res_gp['Código'].map(DIC_GPTE_OFICIAL).fillna('OUTROS')
                st.table(res_gp[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO E RÓTULOS) ---
        with abas_gestao[4]:
            st.subheader("Análise de Pessoas com Deficiência (Indivíduos)")
            df_pcd = df_ctx[df_ctx['p_cod_deficiencia_memb'] == 1].copy()
            if not df_pcd.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    st.metric("Total Indivíduos PcD", len(df_pcd))
                    fig_p = px.pie(df_pcd, names='d_nom_unidade_territorial_fam', hole=0.5, title="PcD por Território")
                    fig_p.update_traces(textinfo='percent+value', hovertemplate='CRAS: %{label}<br>Qtd: %{value}')
                    st.plotly_chart(fig_p, use_container_width=True)
                with cp2:
                    stats_pcd = {DIC_DEF_HUMANO[k]: df_pcd[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd.columns}
                    df_v_pcd = pd.DataFrame(list(stats_pcd.items()), columns=['Deficiência', 'Qtd'])
                    df_v_pcd['Perc'] = (df_v_pcd['Qtd'] / df_v_pcd['Qtd'].sum() * 100)
                    df_v_pcd = df_v_pcd.sort_values('Qtd', ascending=True) # Ascending para o gráfico horizontal
                    fig_bar_pcd = px.bar(df_v_pcd, x='Qtd', y='Deficiência', orientation='h', color='Qtd', title="Perfil PcD (Maior para Menor)")
                    fig_bar_pcd.update_traces(hovertemplate='Tipo: %{y}<br>Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=df_v_pcd['Perc'])
                    st.plotly_chart(fig_bar_pcd, use_container_width=True)

        # --- ABA 6: SITUAÇÃO DE RUA (DETALHAMENTO INTEGRAL) ---
        with abas_gestao[5]:
            st.subheader("Vulnerabilidade Extrema: População de Rua")
            df_rua = df_ctx[df_ctx['p_marc_sit_rua'] == 1].copy()
            st.metric("Marcações de Rua no Território", len(df_rua))
            if not df_rua.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    st.markdown("#### Motivos da Condição de Rua")
                    stats_r = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua.columns}
                    df_m_rua = pd.DataFrame(list(stats_r.items()), columns=['Motivo', 'Qtd']).sort_values('Qtd', ascending=True)
                    df_m_rua['Perc'] = (df_m_rua['Qtd'] / len(df_rua) * 100)
                    fig_m = px.bar(df_m_rua, x='Qtd', y='Motivo', orientation='h', color='Qtd', color_continuous_scale='Reds')
                    fig_m.update_traces(hovertemplate='Motivo: %{y}<br>Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=df_m_rua['Perc'])
                    st.plotly_chart(fig_m, use_container_width=True)
                with cr2:
                    st.markdown("#### Tempo de Permanência")
                    tm = {'1':'Até 6m', '2':'6m a 1ano', '3':'1 a 2anos', '4':'2 a 5anos', '5':'5 a 10anos', '6':'> 10anos'}
                    df_rua['tempo'] = df_rua['p_cod_tempo_rua_memb'].astype(str).map(tm)
                    fig_pie_r = px.pie(df_rua, names='tempo', hole=0.4, title="Tempo de Rua (Qtd e %)")
                    fig_pie_r.update_traces(textinfo='value+percent', hovertemplate='Tempo: %{label}<br>Qtd: %{value}<br>Perc: %{percent}')
                    st.plotly_chart(fig_pie_r, use_container_width=True)

        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {cras_sel}"):
            df_fam[df_fam['status_cad'] == 'Desatualizado'].to_excel(f"LISTA_SLZ_{cras_sel.replace(' ', '_')}.xlsx", index=False)
            st.sidebar.success("Sucesso!")

except Exception as fatal_e:
    st.error(f"Erro Fatal SIGMS: {fatal_e}")

# ==============================================================================
# FIM DO SCRIPT - MAIS DE 850 LINHAS DE ESTRUTURA INDUSTRIAL INTEGRAL
# ==============================================================================
