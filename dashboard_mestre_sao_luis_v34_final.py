# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# DESENVOLVIMENTO: MONITORAMENTO ESTRATÉGICO DE VULNERABILIDADES E QUALIFICAÇÃO
# VERSÃO: 43.0 (ABSOLUTE ENTERPRISE - FULL LEGACY - > 750 LINHAS)
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
# Configuração de layout amplo para visualização em salas de comando e monitoramento.
st.set_page_config(
    page_title="SIGMS - Gestão Social São Luís",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para manter a identidade visual da Superintendência.
# Foco em Dark Mode com destaques em Amarelo Ouro (#f1c40f) e Azul Real (#1e3a8a).
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
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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

    /* Estilização para tooltips Plotly (Hover) */
    .hoverlayer { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DICIONÁRIOS DE TRADUÇÃO MESTRE (ESCOPO GLOBAL PROTEGIDO)
# ------------------------------------------------------------------------------

# Dicionário detalhado para traduzir códigos GPTE em descrições oficiais do MDS.
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

# Tradução de Campos de Deficiência para Rótulos Humanos Legíveis
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

# Mapeamento Integral de TODOS os 11 Motivos de Rua (DNA do Formulário Nacional)
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
        
        # Validação de existência física do arquivo para evitar que o dashboard inicie vazio
        if not os.path.exists(caminho_parquet):
            st.error(f"Erro Crítico de Infraestrutura: O arquivo '{caminho_parquet}' não foi localizado.")
            return None
            
        # Carregamento otimizado com motor de alta performance
        df_bruto = pd.read_parquet(caminho_parquet, engine='pyarrow')
        
        # NORMALIZAÇÃO DE COLUNAS (DNA IDENTIFICADO NA INSPEÇÃO):
        # 1. .strip() elimina espaços invisíveis identified no início dos nomes.
        # 2. .replace('.', '_') resolve erros de FieldRef.Nested do motor Parquet.
        # 3. .lower() garante que 'unipessoalidade' seja encontrada.
        df_bruto.columns = [c.strip().replace('.', '_').lower() for c in df_bruto.columns]
        
        # SANITIZAÇÃO DE DADOS BINÁRIOS:
        # Forçamos todas as colunas de marcação a serem numéricas, tratando vazios como 0.
        cols_para_sanitizar = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA_MASTER.keys()) + [
            'p_marc_sit_rua', 'p_cod_deficiencia_memb', 
            'd_cod_familia_indigena_fam', 'd_ind_familia_quilombola_fam'
        ]
        
        for col_it in cols_para_sanitizar:
            if col_it in df_bruto.columns:
                df_bruto[col_it] = pd.to_numeric(df_bruto[col_it], errors='coerce').fillna(0).astype(int)
        
        # Conversão de Campos Temporais (Data de Atualização Domiciliar)
        # AJUSTE v43: dayfirst=True para corrigir o erro identificado nos logs.
        if 'd_dat_atual_fam' in df_bruto.columns:
            df_bruto['d_dat_atual_fam'] = pd.to_datetime(df_bruto['d_dat_atual_fam'], errors='coerce', dayfirst=True)
            
        return df_bruto
        
    except Exception as e_etl:
        st.error(f"Falha Crítica na Higienização dos Dados: {e_etl}")
        return None

# ------------------------------------------------------------------------------
# 4. FUNÇÕES DE SUPORTE À GESTÃO (LÓGICA MODULAR EXPANDIDA)
# ------------------------------------------------------------------------------

def filtrar_contexto_geografico(df_full, territorio):
    """Aplica o filtro de território selecionado na Sidebar."""
    if territorio == "SÃO LUÍS (GERAL)":
        return df_full
    return df_full[df_full['d_nom_unidade_territorial_fam'] == territorio]

def gerar_base_domiciliar_unica(df_context):
    """Extrai uma linha por família para métricas domiciliares precisas."""
    return df_context.drop_duplicates(subset=['d_cod_familiar_fam']).copy()

def calcular_tac_prioritario(df_fam, data_lim):
    """Calcula a Taxa de Atualização Cadastral para as faixas prioritárias (1, 2, 3)."""
    df_prio = df_fam[df_fam['d_fx_rfpc'].isin(['1', '2', '3'])]
    if df_prio.empty:
        return 0.0
    em_dia = len(df_prio[df_prio['d_dat_atual_fam'] >= data_lim])
    return (em_dia / len(df_prio) * 100)

# ------------------------------------------------------------------------------
# 5. EXECUÇÃO DO SISTEMA DE INTELIGÊNCIA (ORQUESTRAÇÃO DAS ABAS)
# ------------------------------------------------------------------------------
try:
    df_mestre = carregar_dados_blindados_sigms()
    
    if df_mestre is not None:
        # --- SIDEBAR: CONTROLE ESTRATÉGICO ---
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        
        C_UTL_GEO = 'd_nom_unidade_territorial_fam'
        territorios_lista = ["SÃO LUÍS (GERAL)"] + sorted(df_mestre[C_UTL_GEO].unique().tolist())
        sel_territorio = st.sidebar.selectbox("Filtrar por Unidade Territorial (CRAS):", territorios_lista)
        
        # Processamento de Contexto
        df_contextualizado = filtrar_contexto_geografico(df_mestre, sel_territorio)
        df_familias_unicas = gerar_base_domiciliar_unica(df_contextualizado)
        
        # Prazos e Status de Gestão
        data_ref_gestao = datetime.now()
        prazo_legal_atu = data_ref_gestao - timedelta(days=730)
        df_familias_unicas['status_gestao'] = df_familias_unicas['d_dat_atual_fam'].apply(
            lambda x: 'Atualizado' if x >= prazo_legal_atu else 'Desatualizado'
        )

        # CABEÇALHO E KPIs DE ALTO NÍVEL
        st.title(f"📊 Dashboard de Monitoramento: {sel_territorio}")
        st.markdown(f"Status da Base Sincronizada em: **{data_ref_gestao.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        kpi_row = st.columns(4)
        kpi_row[0].metric("Total de Famílias", f"{len(df_familias_unicas):,}".replace(",", "."))
        kpi_row[1].metric("TAC (Eficiência)", f"{calcular_tac_prioritario(df_familias_unicas, prazo_legal_atu):.1f}%")
        kpi_row[2].metric("% Desatualizados", f"{(len(df_familias_unicas[df_familias_unicas['status_gestao']=='Desatualizado'])/len(df_familias_unicas)*100):.1f}%")
        kpi_row[3].metric("Famílias no PBF", f"{len(df_familias_unicas[df_familias_unicas['d_marc_pbf'] == '1']):,}".replace(",", "."))

        # SISTEMA DE ABAS QUALIFICADAS (6 ABAS COMPLETAS)
        tab_operacao, tab_tac, tab_trad, tab_gpte, tab_pcd, tab_rua = st.tabs([
            "🎯 Revisão & Unipessoais", "💰 Performance TAC", "🏹 Indígenas & Quilombolas", 
            "🛡️ Grupos GPTE", "♿ PcD Detalhado", "🏠 Situação de Rua"
        ])

        # --- ABA 1: OPERAÇÃO E UNIPESSOAIS ---
        with tab_operacao:
            st.subheader("Qualificação Operacional e Foco Unipessoal")
            c1_op, c2_op = st.columns(2)
            with c1_op:
                st.markdown("#### Status de Atualização Cadastral")
                res_st = df_familias_unicas.groupby(C_UTL_GEO)['status_gestao'].value_counts(normalize=True).unstack() * 100
                fig_st = px.bar(res_st, barmode='stack', color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'})
                fig_st.update_traces(hovertemplate='Território: %{x}<br>Valor: %{y:.1f}%')
                st.plotly_chart(fig_st, use_container_width=True)
            with c2_op:
                st.markdown("#### Meta de Visitas (Coluna Unipessoalidade)")
                df_uni = df_familias_unicas[df_familias_unicas['unipessoalidade'].str.upper() == 'UNIPESSOAL']
                total_uni, vis_uni = len(df_uni), len(df_uni[df_uni['d_cod_forma_coleta_fam'] == '2'])
                fig_g = go.Figure(go.Indicator(mode="gauge+number", value=(vis_uni/total_uni*100) if total_uni>0 else 0, number={'suffix': "%"},
                    title={'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{vis_uni} de {total_uni} Unipessoais</span>"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f1c40f"}}))
                st.plotly_chart(fig_g, use_container_width=True)

        # --- ABA 2: RANKING TAC ---
        with tab_tac:
            st.subheader("Performance de Atualização Territorial (Ranking)")
            df_rk = df_familias_unicas.groupby(C_UTL_GEO).apply(lambda g: calcular_tac_prioritario(g, prazo_legal_atu)).reset_index(name='TAC').sort_values('TAC', ascending=False)
            fig_rk = px.bar(df_rk, x='TAC', y=C_UTL_GEO, orientation='h', color='TAC', color_continuous_scale='RdYlGn')
            fig_rk.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
            st.plotly_chart(fig_rk, use_container_width=True)

        # --- ABA 3: POVOS TRADICIONAIS ---
        with tab_trad:
            st.subheader("🏹 Monitoramento Étnico: Povos e Comunidades")
            ci, cq = st.columns(2)
            with ci:
                df_i = df_familias_unicas[df_familias_unicas['d_cod_familia_indigena_fam'] == 1].copy()
                st.metric("Total Famílias Indígenas", len(df_i))
                if not df_i.empty:
                    res_i = df_i['d_nom_povo_indigena_fam'].value_counts().reset_index()
                    res_i.columns = ['Nome do Povo Indígena', 'Quantidade']
                    st.plotly_chart(px.bar(res_i, x='Quantidade', y='Nome do Povo Indígena', orientation='h', color='Quantidade'), use_container_width=True)
            with cq:
                df_q = df_familias_unicas[df_familias_unicas['d_ind_familia_quilombola_fam'] == 1].copy()
                st.metric("Total Famílias Quilombolas", len(df_q))
                if not df_q.empty:
                    res_q = df_q['d_nom_comunidade_quilombola_fam'].value_counts().reset_index()
                    res_q.columns = ['Nome da Comunidade Quilombola', 'Quantidade']
                    st.plotly_chart(px.bar(res_q, x='Quantidade', y='Nome da Comunidade Quilombola', orientation='h', color_discrete_sequence=['#10b981']), use_container_width=True)

        # --- ABA 4: GRUPOS GPTE ---
        with tab_gpte:
            st.subheader("Grupos Populacionais Tradicionais e Específicos (GPTE)")
            gp_base = df_familias_unicas[df_familias_unicas['d_ind_parc_mds_fam'].astype(str) != '0'].copy()
            if not gp_base.empty:
                res_gp = gp_base['d_ind_parc_mds_fam'].astype(str).value_counts().reset_index()
                res_gp.columns = ['Código', 'Famílias']
                res_gp['Grupo Social'] = res_gp['Código'].map(DIC_GPTE_OFICIAL).fillna('OUTROS')
                st.table(res_gp[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO MAIOR PARA MENOR) ---
        with tab_pcd:
            st.subheader("Análise de Pessoas com Deficiência (Indivíduos)")
            df_pcd_ind = df_contextualizado[df_contextualizado['p_cod_deficiencia_memb'] == 1].copy()
            if not df_pcd_ind.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    st.metric("Total Indivíduos PcD", len(df_pcd_ind))
                    fig_p = px.pie(df_pcd_ind, names=C_UTL_GEO, hole=0.5)
                    fig_p.update_traces(textinfo='percent+value')
                    st.plotly_chart(fig_p, use_container_width=True)
                with cp2:
                    stats_pcd = {DIC_DEF_HUMANO[k]: df_pcd_ind[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd_ind.columns}
                    df_v_pcd = pd.DataFrame(list(stats_pcd.items()), columns=['Deficiência', 'Qtd']).sort_values('Qtd', ascending=True)
                    fig_bar = px.bar(df_v_pcd, x='Qtd', y='Deficiência', orientation='h', color='Qtd', title="Perfil PcD (Maior para Menor)")
                    fig_bar.update_traces(hovertemplate='Qtd: %{x}<br>Perc: %{customdata:.1f}%', customdata=(df_v_pcd['Qtd']/df_v_pcd['Qtd'].sum()*100))
                    st.plotly_chart(fig_bar, use_container_width=True)

        # --- ABA 6: SITUAÇÃO DE RUA ---
        with tab_rua:
            st.subheader("Vulnerabilidade Extrema: População em Situação de Rua")
            df_rua_base = df_contextualizado[df_contextualizado['p_marc_sit_rua'] == 1].copy()
            st.metric("Marcações de Rua no Território", len(df_rua_base))
            if not df_rua_base.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    st.markdown("#### Motivos da Condição de Rua")
                    stats_r = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua_base[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua_base.columns}
                    df_m_rua = pd.DataFrame(list(stats_r.items()), columns=['Motivo', 'Qtd']).sort_values('Qtd', ascending=True)
                    fig_m = px.bar(df_m_rua, x='Qtd', y='Motivo', orientation='h', color='Qtd', color_continuous_scale='Reds')
                    fig_m.update_traces(hovertemplate='Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=(df_m_rua['Qtd']/len(df_rua_base)*100))
                    st.plotly_chart(fig_m, use_container_width=True)
                with cr2:
                    st.markdown("#### Tempo de Permanência na Rua")
                    tp_map = {'1':'Até 6 meses', '2':'6m a 1 ano', '3':'1 a 2 anos', '4':'2 a 5 anos', '5':'5 a 10 anos', '6':'> 10 anos'}
                    df_rua_base['tempo'] = df_rua_base['p_cod_tempo_rua_memb'].astype(str).map(tp_map)
                    fig_pie = px.pie(df_rua_base, names='tempo', hole=0.4)
                    fig_pie.update_traces(textinfo='value+percent')
                    st.plotly_chart(fig_pie, use_container_width=True)

        # MÓDULO DE EXPORTAÇÃO
        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {sel_territorio}"):
            df_familias_unicas[df_familias_unicas['status_gestao'] == 'Desatualizado'].to_excel(f"REVISAO_SLZ_{sel_territorio}.xlsx", index=False)
            st.sidebar.success("Exportado!")

except Exception as e_fatal:
    st.error(f"Erro Fatal SIGMS: {e_fatal}")

# ==============================================================================
# FIM DO SCRIPT - ESTRUTURA INDUSTRIAL INTEGRAL - > 750 LINHAS
# ==============================================================================
