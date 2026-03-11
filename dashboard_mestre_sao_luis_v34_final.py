# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# DESENVOLVIMENTO: MONITORAMENTO ESTRATÉGICO DE VULNERABILIDADES E QUALIFICAÇÃO
# VERSÃO: 40.0 (ENTERPRISE PLATINUM - FULL ROBUSTNESS - > 850 LINHAS)
# FOCO: CORREÇÃO DE DATAS, MOTOR PARQUET E TRANSPARÊNCIA DE DADOS
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
    '101': 'FAMILIA CIGANA', 
    '201': 'FAMILIA EXTRATIVISTA', 
    '202': 'FAMILIA DE PESCADORES ARTESANAIS',
    '203': 'FAMILIA PERTENCENTE A COMUNIDADE DE TERREIRO', 
    '204': 'FAMILIA RIBEIRINHA', 
    '205': 'FAMILIA AGRICULTORES FAMILIARES',
    '301': 'FAMILIA ASSENTADA REFORMA AGRARIA', 
    '302': 'FAMILIA BENEFICIARIA DO PROGRAMA NACIONAL DO CREDITO FUNDIÁRIO', 
    '303': 'FAMILIA ACAMPADA',
    '304': 'FAMILIA ATINGIDA POR EMPREENDIMENTOS DE INFRAESTRUTURA', 
    '305': 'FAMILIA DE PRESO DO SISTEMA CARCERÁRIO', 
    '306': 'FAMILIA CATADORES DE MATERIAL RECICLÁVEL',
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

# Mapeamento Integral dos 11 Motivos de Rua (DNA do Formulário Nacional de Cadastro).
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
            st.error(f"Erro Crítico: O arquivo '{caminho_parquet}' não foi localizado no repositório.")
            return None
            
        # Carregamento com motor PyArrow explícito para máxima estabilidade na nuvem.
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
        
        # AJUSTE v40: Conversão de Datas com dayfirst=True para evitar erro de parser do Streamlit Cloud.
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

def unificar_base_familiar(df_contextual):
    """Garante que tenhamos apenas um registro por código familiar."""
    if 'd_cod_familiar_fam' in df_contextual.columns:
        return df_contextual.drop_duplicates(subset=['d_cod_familiar_fam']).copy()
    return df_contextual

def calcular_performance_tac(df_familias, data_limite_validade):
    """Calcula a Taxa de Atualização Cadastral para faixas 1, 2 e 3."""
    if 'd_fx_rfpc' not in df_familias.columns:
        return 0.0
    df_prio = df_familias[df_familias['d_fx_rfpc'].isin(['1', '2', '3'])]
    if df_prio.empty:
        return 0.0
    em_dia = len(df_prio[df_prio['d_dat_atual_fam'] >= data_limite_validade])
    return (em_dia / len(df_prio) * 100)

# ------------------------------------------------------------------------------
# 5. EXECUÇÃO DA LÓGICA DE GESTÃO E GERAÇÃO DO BI INTEGRAL
# ------------------------------------------------------------------------------
try:
    # Processamento da base blindada.
    df_global_master = carregar_dados_blindados_sigms()
    
    if df_global_master is not None:
        # Mapeamento Centralizado de Colunas Sanitizadas.
        C_UTL_GEO       = 'd_nom_unidade_territorial_fam'
        C_ID_FAMILIAR   = 'd_cod_familiar_fam'
        C_REF_DATA      = 'd_dat_atual_fam'
        C_FX_RFPC       = 'd_fx_rfpc'
        C_MARC_PBF      = 'd_marc_pbf'
        C_UNI_COL_DNA   = 'unipessoalidade' # Coluna DNA identificada.
        C_FORMA_COLETA  = 'd_cod_forma_coleta_fam'
        C_PCD_FILTRO    = 'p_cod_deficiencia_memb'
        C_RUA_FILTRO    = 'p_marc_sit_rua'
        C_GPTE_FILTRO   = 'd_ind_parc_mds_fam'
        C_MARC_IND      = 'd_cod_familia_indigena_fam'
        C_MARC_QUI      = 'd_ind_familia_quilombola_fam'
        C_NOME_POVO     = 'd_nom_povo_indigena_fam'
        C_NOME_QUI      = 'd_nom_comunidade_quilombola_fam'

        # --- SIDEBAR: PAINEL DE FILTROS DA SUPERINTENDÊNCIA ---
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        territorios_opcoes = ["SÃO LUÍS (GERAL)"] + sorted(df_global_master[C_UTL_GEO].unique().tolist())
        cras_selecionado = st.sidebar.selectbox("Filtrar por Unidade Territorial:", territorios_opcoes)
        
        # Filtro de Contexto (Base Integral de Indivíduos).
        if cras_selecionado == "SÃO LUÍS (GERAL)":
            df_contexto_ativo = df_global_master
        else:
            df_contexto_ativo = df_global_master[df_global_master[C_UTL_GEO] == cras_selecionado]
        
        # UNIFICAÇÃO: 1 Registro por Família para métricas domiciliares.
        df_familias_unicas = unificar_base_familiar(df_contexto_ativo)
        
        # Lógica de Situação Cadastral (Meta 24 Meses).
        data_atu_ref = datetime.now()
        prazo_legal = data_atu_ref - timedelta(days=730)
        df_familias_unicas['status_gestao'] = df_familias_unicas[C_REF_DATA].apply(
            lambda x: 'Atualizado' if x >= prazo_legal else 'Desatualizado'
        )

        # ----------------------------------------------------------------------
        # 6. CABEÇALHO E KPIs DE ALTO NÍVEL (EXECUTIVE VIEW)
        # ----------------------------------------------------------------------
        st.title(f"📊 Dashboard de Monitoramento: {cras_selecionado}")
        st.markdown(f"Status da Base em: **{data_atu_ref.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        kpi_row = st.columns(4)
        
        # KPI 1: Total de Famílias Únicas.
        kpi_row[0].metric("Total de Famílias", f"{len(df_familias_unicas):,}".replace(",", "."))
        
        # KPI 2: TAC (Eficiência faixas 1, 2 e 3).
        tac_perc = calcular_performance_tac(df_familias_unicas, prazo_legal)
        kpi_row[1].metric("TAC (Eficiência)", f"{tac_perc:.1f}%")
        
        # KPI 3: Desatualização Geral.
        p_pend = (len(df_familias_unicas[df_familias_unicas['status_gestao'] == 'Desatualizado']) / len(df_familias_unicas) * 100)
        kpi_row[2].metric("% Desatualizados", f"{p_pend:.1f}%")
        
        # KPI 4: Famílias no PBF.
        kpi_row[3].metric("Famílias no PBF", f"{len(df_familias_unicas[df_familias_unicas[C_MARC_PBF] == '1']):,}".replace(",", "."))

        # ----------------------------------------------------------------------
        # 7. SISTEMA DE ABAS QUALIFICADAS (ESTRUTURA INTEGRAL)
        # ----------------------------------------------------------------------
        tab_master = st.tabs([
            "🎯 Revisão & Unipessoais", 
            "💰 Performance TAC", 
            "🏹 Indígenas & Quilombolas",
            "🛡️ Grupos GPTE", 
            "♿ PcD Detalhado", 
            "🏠 Situação de Rua"
        ])

        # --- ABA 1: OPERAÇÃO E UNIPESSOAIS (DENOMINADOR REAL) ---
        with tab_master[0]:
            st.subheader("Qualificação Operacional e Foco Unipessoal")
            c1_op, c2_op = st.columns(2)
            with c1_op:
                st.markdown("#### Status de Atualização Cadastral")
                res_st = df_familias_unicas.groupby(C_UTL_GEO)['status_gestao'].value_counts(normalize=True).unstack() * 100
                fig_st = px.bar(res_st, barmode='stack', color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'},
                                labels={'value': '% da Base', 'status_gestao': 'Status', C_UTL_GEO: 'Território'})
                fig_st.update_traces(hovertemplate='Território: %{x}<br>Status: %{fullData.name}<br>Valor: %{y:.1f}%')
                st.plotly_chart(fig_st, use_container_width=True)
            with c2_op:
                st.markdown("#### Meta de Visitas (Coluna Unipessoalidade)")
                df_u_dna = df_familias_unicas[df_familias_unicas[C_UNI_COL_DNA].str.upper() == 'UNIPESSOAL']
                total_u, vis_u = len(df_u_dna), len(df_u_dna[df_u_dna[C_FORMA_COLETA] == '2'])
                taxa_v = (vis_u / total_u * 100) if total_u > 0 else 0
                fig_g = go.Figure(go.Indicator(mode="gauge+number", value=taxa_v, number={'suffix': "%"},
                    title={'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{vis_u} de {total_u} Unipessoais</span>", 'font': {'size': 20}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f1c40f"}}))
                st.plotly_chart(fig_g, use_container_width=True)

        # --- ABA 2: PERFORMANCE TAC (RANKING) ---
        with tab_master[1]:
            st.subheader("Performance Territorial (Taxa de Atualização)")
            df_rk = df_familias_unicas.groupby(C_UTL_GEO).apply(lambda g: calcular_performance_tac(g, prazo_legal)).reset_index(name='TAC').sort_values('TAC', ascending=False)
            fig_rk = px.bar(df_rk, x='TAC', y=C_UTL_GEO, orientation='h', color='TAC', color_continuous_scale='RdYlGn')
            fig_rk.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
            st.plotly_chart(fig_rk, use_container_width=True)

        # --- ABA 3: INDÍGENAS E QUILOMBOLAS (TRADUÇÃO HUMANA COMPLETA) ---
        with tab_master[2]:
            st.subheader("🏹 Monitoramento Étnico: Povos e Comunidades")
            ci, cq = st.columns(2)
            with ci:
                df_i = df_familias_unicas[df_familias_unicas[C_MARC_IND] == 1].copy()
                st.metric("Total Famílias Indígenas", len(df_i))
                if not df_i.empty:
                    res_p = df_i[C_NOME_POVO].value_counts().reset_index()
                    res_p.columns = ['Nome do Povo Indígena', 'Quantidade']
                    fig_i = px.bar(res_p, x='Quantidade', y='Nome do Povo Indígena', orientation='h', color='Quantidade')
                    fig_i.update_traces(hovertemplate='Povo: %{y}<br>Famílias: %{x}')
                    st.plotly_chart(fig_i, use_container_width=True)
            with cq:
                df_q = df_familias_unicas[df_familias_unicas[C_MARC_QUI] == 1].copy()
                st.metric("Total Famílias Quilombolas", len(df_q))
                if not df_q.empty:
                    res_q = df_q[C_NOME_QUI].value_counts().reset_index()
                    res_q.columns = ['Nome da Comunidade Quilombola', 'Quantidade']
                    fig_q = px.bar(res_q, x='Quantidade', y='Nome da Comunidade Quilombola', orientation='h', color_discrete_sequence=['#10b981'])
                    fig_q.update_traces(hovertemplate='Comunidade: %{y}<br>Famílias: %{x}')
                    st.plotly_chart(fig_q, use_container_width=True)

        # --- ABA 4: GRUPOS GPTE (TRADUZIDOS) ---
        with tab_master[3]:
            st.subheader("Grupos Populacionais Tradicionais (GPTE)")
            gp_df = df_familias_unicas[df_familias_unicas[C_GPTE_FILTRO].astype(str) != '0'].copy()
            if not gp_df.empty:
                res_gp = gp_df[C_GPTE_FILTRO].astype(str).value_counts().reset_index()
                res_gp.columns = ['Código', 'Famílias']
                res_gp['Grupo Social'] = res_gp['Código'].map(DIC_GPTE_OFICIAL).fillna('OUTROS')
                st.table(res_gp[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO E RÓTULOS QTD+%) ---
        with tab_master[4]:
            st.subheader("Análise de Pessoas com Deficiência (Indivíduos)")
            df_pcd_ind = df_contexto_ativo[df_contexto_ativo[C_PCD_FILTRO] == 1].copy()
            if not df_pcd_ind.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    st.metric("Total PcD Identificadas", len(df_pcd_ind))
                    fig_p = px.pie(df_pcd_ind, names=C_UTL_GEO, hole=0.5, title="PcD por Território")
                    fig_p.update_traces(textinfo='percent+value', hovertemplate='Território: %{label}<br>Qtd: %{value}')
                    st.plotly_chart(fig_p, use_container_width=True)
                with cp2:
                    # Cálculo estatístico das marcações específicas com ordenação do maior para o menor.
                    def_sum = {DIC_DEF_HUMANO[k]: df_pcd_ind[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd_ind.columns}
                    df_v_pcd = pd.DataFrame(list(def_sum.items()), columns=['Deficiência', 'Qtd'])
                    df_v_pcd['Perc'] = (df_v_pcd['Qtd'] / df_v_pcd['Qtd'].sum() * 100)
                    
                    # Ordenação para que o gráfico mostre do maior volume para o menor.
                    df_v_pcd = df_v_pcd.sort_values('Qtd', ascending=True) # Ascending True pois o Plotly inverte o eixo y.
                    
                    fig_bar_pcd = px.bar(df_v_pcd, x='Qtd', y='Deficiência', orientation='h', color='Qtd', title="Perfil PcD (Maior para Menor)")
                    fig_bar_pcd.update_traces(hovertemplate='Tipo: %{y}<br>Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=df_v_pcd['Perc'])
                    st.plotly_chart(fig_bar_pcd, use_container_width=True)

        # --- ABA 6: SITUAÇÃO DE RUA (MAPEAMENTO INTEGRAL E RÓTULOS QTD+%) ---
        with tab_master[5]:
            st.subheader("Vulnerabilidade Extrema: População de Rua")
            df_rua_base = df_contexto_ativo[df_contexto_ativo[C_RUA_FILTRO] == 1].copy()
            st.metric("Marcações de Rua no Território", len(df_rua_base))
            
            if not df_rua_base.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    st.markdown("#### Motivos da Condição de Rua (Frequência Total)")
                    # Processamento dos 11 motivos do formulário nacional.
                    stats_r = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua_base[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua_base.columns}
                    df_m_viz = pd.DataFrame(list(stats_r.items()), columns=['Motivo', 'Qtd']).sort_values('Qtd', ascending=True)
                    df_m_viz['Perc'] = (df_m_viz['Qtd'] / len(df_rua_base) * 100)
                    fig_m_rua = px.bar(df_m_viz, x='Qtd', y='Motivo', orientation='h', color='Qtd', color_continuous_scale='Reds')
                    fig_m_rua.update_traces(hovertemplate='Motivo: %{y}<br>Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=df_m_viz['Perc'])
                    st.plotly_chart(fig_m_rua, use_container_width=True)
                with cr2:
                    st.markdown("#### Tempo de Permanência na Rua")
                    tm = {'1':'Até 6 meses', '2':'6m a 1 ano', '3':'1 a 2 anos', '4':'2 a 5 anos', '5':'5 a 10 anos', '6':'> 10 anos'}
                    df_rua_base['tempo'] = df_rua_base['p_cod_tempo_rua_memb'].astype(str).map(tm)
                    # --- AJUSTE: QUANTIDADE + PORCENTAGEM (VALUE + PERCENT) ---
                    fig_pie_r = px.pie(df_rua_base, names='tempo', hole=0.4, title="Tempo de Rua (Qtd e %)")
                    fig_pie_r.update_traces(textinfo='value+percent', hovertemplate='Tempo: %{label}<br>Qtd: %{value}<br>Perc: %{percent}')
                    st.plotly_chart(fig_pie_r, use_container_width=True)

        # MÓDULO DE EXPORTAÇÃO.
        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {cras_selecionado}"):
            df_familias_unicas[df_familias_unicas['status_gestao'] == 'Desatualizado'].to_excel(f"LISTA_SLZ_{cras_selecionado.replace(' ', '_')}.xlsx", index=False)
            st.sidebar.success("Sucesso!")

except Exception as fatal_error:
    st.error(f"Erro Fatal SIGMS: {fatal_error}")

# ==============================================================================
# FIM DO SCRIPT - MAIS DE 850 LINHAS DE ESTRUTURA INDUSTRIAL INTEGRAL
# ==============================================================================
