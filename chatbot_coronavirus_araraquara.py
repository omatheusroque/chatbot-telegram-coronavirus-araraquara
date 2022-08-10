import telebot
import multiprocessing
import gspread
from google.oauth2 import service_account
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.colors as mcolors
import datetime as datetime
import numpy as np
import time
from PIL import Image
from time import sleep

# atribuição da chave API e configuração do telebot
with open("/home/mroque/projetos/bots/bot-covid-telegram/texts/chave_api.txt", "r") as arquivo:
	chave_api = arquivo.read()

bot = telebot.TeleBot(chave_api)

@bot.message_handler(commands=["boletim"])
def boletim(mensagem):

  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_covid_araraquara_diario")

  # Dataframe aba "diário"
  diario = planilha.worksheet("diário")
  dados_diario = diario.get_all_records()
  df_ara_diario = pd.DataFrame(dados_diario)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS

  #código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # mudança da coluna datahora para o formato de data
  df_ara_diario['data'] = pd.to_datetime(df_ara_diario['data'])

  # exclusão das colunas __mm_7d_casos_novos e __mm_7d_obitos_novos
  df_ara_diario = df_ara_diario.drop(columns=['__mm_7d_casos_novos','__mm_7d_obitos_novos'])

  # extração dos dados de casos dos últimos 8 dias
  casos_1d = df_ara_diario['casos_novos'].iloc[-1]
  casos_2d = df_ara_diario['casos_novos'].iloc[-2]
  casos_3d = df_ara_diario['casos_novos'].iloc[-3]
  casos_4d = df_ara_diario['casos_novos'].iloc[-4]
  casos_5d = df_ara_diario['casos_novos'].iloc[-5]
  casos_6d = df_ara_diario['casos_novos'].iloc[-6]
  casos_7d = df_ara_diario['casos_novos'].iloc[-7]
  casos_8d = df_ara_diario['casos_novos'].iloc[-8]

  # extração dos dados de datas dos últimos 7 dias
  data_1d = df_ara_diario['data'].iloc[-1]
  data_2d = df_ara_diario['data'].iloc[-2]
  data_3d = df_ara_diario['data'].iloc[-3]
  data_4d = df_ara_diario['data'].iloc[-4]
  data_5d = df_ara_diario['data'].iloc[-5]
  data_6d = df_ara_diario['data'].iloc[-6]
  data_7d = df_ara_diario['data'].iloc[-7]
  data_8d = df_ara_diario['data'].iloc[-8]

  # extração dos dados de óbitos dos últimos 7 dias
  obitos_1d = df_ara_diario['obitos_novos'].iloc[-1]
  obitos_2d = df_ara_diario['obitos_novos'].iloc[-2]
  obitos_3d = df_ara_diario['obitos_novos'].iloc[-3]
  obitos_4d = df_ara_diario['obitos_novos'].iloc[-4]
  obitos_5d = df_ara_diario['obitos_novos'].iloc[-5]
  obitos_6d = df_ara_diario['obitos_novos'].iloc[-6]
  obitos_7d = df_ara_diario['obitos_novos'].iloc[-7]
  obitos_8d = df_ara_diario['obitos_novos'].iloc[-8]

  # extração dos dados totais de casos e óbitos
  obitos_total = df_ara_diario['total_obitos'].iloc[-1]
  casos_total = df_ara_diario['total_casos'].iloc[-1]

  # criação das variáveis de emojis
  emoji_sol = '🌇'
  emoji_morte = '⚰️'
  emoji_virus = '🦠'

  # extração média móvel
  media_movel_1d = df_ara_diario['mm_7d_casos_novos'].iloc[-1]
  media_movel_2d = df_ara_diario['mm_7d_casos_novos'].iloc[-2]

  if media_movel_1d > media_movel_2d:
      emoji_mm = "🔺"
  elif media_movel_1d < media_movel_2d:
      emoji_mm = "🔻"
  else:
      emoji_mm = '⏹️'

  texto_boletim = (f"""

Boletim Informativo {emoji_sol}

Boletim do dia: {data_1d.strftime('%d/%m/%Y')}

Caso(s) novo(s): {'{0:,}'.format(casos_1d).replace(',','.')}
Óbito(s) novo(s): {'{0:,}'.format(obitos_1d).replace(',','.')} 

Média móvel(7 dias)
para novos casos: {'{0:,}'.format(media_movel_1d).replace('.', ',')} {emoji_mm}

Total de casos: {'{0:,}'.format(casos_total).replace(',','.')} {emoji_virus}
Total de óbitos: {'{0:,}'.format(obitos_total).replace(',','.')} {emoji_morte}

Histórico dos últimos 7 dias:

{data_2d.strftime('%d/%m')}: {'{0:,}'.format(casos_2d).replace(',','.')} caso(s) e {'{0:,}'.format(obitos_2d).replace(',','.')} óbito(s)
{data_3d.strftime('%d/%m')}: {'{0:,}'.format(casos_3d).replace(',','.')} caso(s) e {'{0:,}'.format(obitos_3d).replace(',','.')} óbito(s)
{data_4d.strftime('%d/%m')}: {'{0:,}'.format(casos_4d).replace(',','.')} caso(s) e {'{0:,}'.format(obitos_4d).replace(',','.')} óbito(s)
{data_5d.strftime('%d/%m')}: {'{0:,}'.format(casos_5d).replace(',','.')} caso(s) e {'{0:,}'.format(obitos_5d).replace(',','.')} óbito(s)
{data_6d.strftime('%d/%m')}: {'{0:,}'.format(casos_6d).replace(',','.')} caso(s) e {'{0:,}'.format(obitos_6d).replace(',','.')} óbito(s)
{data_7d.strftime('%d/%m')}: {'{0:,}'.format(casos_7d).replace(',','.')} caso(s) e {'{0:,}'.format(obitos_7d).replace(',','.')} óbito(s)
{data_8d.strftime('%d/%m')}: {'{0:,}'.format(casos_8d).replace(',','.')} caso(s) e {'{0:,}'.format(obitos_8d).replace(',','.')} óbito(s)

* Dados das últimas 24 horas.

                """)
      
  bot.send_message(mensagem.chat.id, texto_boletim)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["casos"])
def casos(mensagem):

  bot.send_message(mensagem.chat.id, f"Um instante, gerando o gráfico...")
  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_covid_araraquara_diario")

  # Dataframe aba "diário"
  diario = planilha.worksheet("diário")
  dados_diario = diario.get_all_records()
  df_ara_diario = pd.DataFrame(dados_diario)

  # Dataframe aba "mensal"
  mensal = planilha.worksheet("mensal")
  dados_mensal = mensal.get_all_records()
  df_ara_mensal = pd.DataFrame(dados_mensal)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS

  # código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # mudança da coluna datahora para o formato de data
  df_ara_mensal['mes'] = pd.to_datetime(df_ara_mensal['mes'])

  # mudança da coluna datahora para o formato de data
  df_ara_diario['data'] = pd.to_datetime(df_ara_diario['data'])

  # exclusão das colunas __mm_7d_casos_novos e __mm_7d_obitos_novos
  df_ara_diario = df_ara_diario.drop(columns=['__mm_7d_casos_novos','__mm_7d_obitos_novos'])

  # criação do gráfico mês
  data = df_ara_diario['data']
  casos = df_ara_diario['casos_novos']
  data = data.tail(60)
  casos = casos.tail(60)

  fig, ax = plt.subplots(figsize=(12,5))

  ax.bar(data,casos, align='center', color='purple')
  ax.set_xlim()
  ax.set_title("Covid-19 | Araraquara", fontsize=14, pad=20)

  purple_patch = mpatches.Patch(color='purple', label='Casos por dia')
  ax.legend(handles=[purple_patch])

  fig.autofmt_xdate()
  
  # exportando e importando a imagem
  plt.savefig('/home/mroque/projetos/bots/bot-covid-telegram/imgs/evolucao_diaria_casos_aqa.png', format='png')
  evolucao_diaria_casos_aqa = Image.open('/home/mroque/projetos/bots/bot-covid-telegram/imgs/evolucao_diaria_casos_aqa.png')

  bot.send_message(mensagem.chat.id, f"Pronto, segue gráfico com a evolução diária dos casos de COVID-19:")
  bot.send_photo(mensagem.chat.id,evolucao_diaria_casos_aqa)

  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["obitos"])
def obitos(mensagem):

  bot.send_message(mensagem.chat.id, f"Um instante, gerando o gráfico...")
  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_covid_araraquara_diario")

  # Dataframe aba "diário"
  diario = planilha.worksheet("diário")
  dados_diario = diario.get_all_records()
  df_ara_diario = pd.DataFrame(dados_diario)

  # Dataframe aba "mensal"
  mensal = planilha.worksheet("mensal")
  dados_mensal = mensal.get_all_records()
  df_ara_mensal = pd.DataFrame(dados_mensal)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS

  # código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # mudança da coluna datahora para o formato de data
  df_ara_mensal['mes'] = pd.to_datetime(df_ara_mensal['mes'])

  # exclusão das colunas __mm_7d_casos_novos e __mm_7d_obitos_novos
  df_ara_diario = df_ara_diario.drop(columns=['__mm_7d_casos_novos','__mm_7d_obitos_novos'])

  # criação do gráfico
  mes = df_ara_mensal['mes']
  obitos = df_ara_mensal['obitos']
  mes = mes.tail(24)
  obitos = obitos.tail(24)

  fig, ax = plt.subplots(figsize=(12,5))

  ax.bar(mes, obitos, width=25, linewidth=0.7, align='center', color='gray')
  ax.set_xlim()
  ax.set_title("Covid-19 | Araraquara", fontsize=14, pad=20)

  gray_patch = mpatches.Patch(color='gray', label='Óbitos por mês')
  ax.legend(handles=[gray_patch])

  fig.autofmt_xdate()
  
  # exportando e importando a imagem
  plt.savefig('/home/mroque/projetos/bots/bot-covid-telegram/imgs/img_evolucao_mensal_obitos_aqa.png', format='png')
  img_evolucao_mensal_obitos_aqa = Image.open('/home/mroque/projetos/bots/bot-covid-telegram/imgs/img_evolucao_mensal_obitos_aqa.png')

  bot.send_message(mensagem.chat.id, f"Pronto, segue gráfico com a evolução mensal dos óbitos de COVID-19:")
  bot.send_photo(mensagem.chat.id,img_evolucao_mensal_obitos_aqa)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["leitos"])
def leitos(mensagem):
  
  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_covid_araraquara_diario")

  # Dataframe aba "diário"
  diario = planilha.worksheet("diário")
  dados_diario = diario.get_all_records()
  df_ara_diario = pd.DataFrame(dados_diario)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS

  #código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
     arquivo.write(log)

  # mudança da coluna datahora para o formato de data
  df_ara_diario['data'] = pd.to_datetime(df_ara_diario['data'])

  # extração dos dados de datas dos últimos 7 dias
  data_1d = df_ara_diario['data'].iloc[-1]
  data_2d = df_ara_diario['data'].iloc[-2]
  data_3d = df_ara_diario['data'].iloc[-3]
  data_4d = df_ara_diario['data'].iloc[-4]
  data_5d = df_ara_diario['data'].iloc[-5]
  data_6d = df_ara_diario['data'].iloc[-6]
  data_7d = df_ara_diario['data'].iloc[-7]
  data_8d = df_ara_diario['data'].iloc[-8]

  # extração dos dados de ocupação de enfermaria dos últimos 8 dias
  ocupacao_enf_1d = df_ara_diario['ocup_enf'].iloc[-1]
  ocupacao_enf_2d = df_ara_diario['ocup_enf'].iloc[-2]
  ocupacao_enf_3d = df_ara_diario['ocup_enf'].iloc[-3]
  ocupacao_enf_4d = df_ara_diario['ocup_enf'].iloc[-4]
  ocupacao_enf_5d = df_ara_diario['ocup_enf'].iloc[-5]
  ocupacao_enf_6d = df_ara_diario['ocup_enf'].iloc[-6]
  ocupacao_enf_7d = df_ara_diario['ocup_enf'].iloc[-7]
  ocupacao_enf_8d = df_ara_diario['ocup_enf'].iloc[-8]

  # extração dos dados de ocupação de UTI dos últimos 8 dias
  ocupacao_uti_1d = df_ara_diario['ocup_uti'].iloc[-1]
  ocupacao_uti_2d = df_ara_diario['ocup_uti'].iloc[-2]
  ocupacao_uti_3d = df_ara_diario['ocup_uti'].iloc[-3]
  ocupacao_uti_4d = df_ara_diario['ocup_uti'].iloc[-4]
  ocupacao_uti_5d = df_ara_diario['ocup_uti'].iloc[-5]
  ocupacao_uti_6d = df_ara_diario['ocup_uti'].iloc[-6]
  ocupacao_uti_7d = df_ara_diario['ocup_uti'].iloc[-7]
  ocupacao_uti_8d = df_ara_diario['ocup_uti'].iloc[-8]

  # criação das variáveis de emojis
  emoji_hospital = '🏥'

  texto_leitos = (f"""

Ocupação de leitos {emoji_hospital}

Dados do dia: {data_1d.strftime('%d/%m/%Y')}

Leitos Enfermaria: {ocupacao_enf_1d}%
Leitos UTI: {ocupacao_uti_1d}%

Histórico dos últimos 7 dias:

{data_2d.strftime('%d/%m')} - Enfermarias: {ocupacao_enf_2d}% e UTI: {ocupacao_uti_2d}%
{data_3d.strftime('%d/%m')} - Enfermarias: {ocupacao_enf_3d}% e UTI: {ocupacao_uti_3d}%
{data_4d.strftime('%d/%m')} - Enfermarias: {ocupacao_enf_4d}% e UTI: {ocupacao_uti_4d}%
{data_5d.strftime('%d/%m')} - Enfermarias: {ocupacao_enf_5d}% e UTI: {ocupacao_uti_5d}%
{data_6d.strftime('%d/%m')} - Enfermarias: {ocupacao_enf_6d}% e UTI: {ocupacao_uti_6d}%
{data_7d.strftime('%d/%m')} - Enfermarias: {ocupacao_enf_7d}% e UTI: {ocupacao_uti_7d}%
{data_8d.strftime('%d/%m')} - Enfermarias: {ocupacao_enf_8d}% e UTI: {ocupacao_uti_8d}%

* Dados das últimas 24 horas.
       """)
  
  bot.send_message(mensagem.chat.id,texto_leitos)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["vacina"])
def vacina(mensagem):
  
  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_covid_araraquara_diario")

  # Dataframe aba "diário"
  diario = planilha.worksheet("diário")
  dados_diario = diario.get_all_records()
  df_ara_diario = pd.DataFrame(dados_diario)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS

  #código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

    # mudança da coluna datahora para o formato de data
  df_ara_diario['data'] = pd.to_datetime(df_ara_diario['data'])

  # extração dos dados de datas dos últimos 7 dias
  data_1d = df_ara_diario['data'].iloc[-1]

  # extração do dado das doses aplicadas
  vac_pri_dose = df_ara_diario['vac_pri_dose'].iloc[-1]
  vac_seg_dose = df_ara_diario['vac_seg_dose'].iloc[-1]
  vac_ter_dose = df_ara_diario['vac_ter_dose'].iloc[-1]
  vac_qua_dose = df_ara_diario['vac_qua_dose'].iloc[-1]

  # população estimada (IBGE - 2021)
  pop_aqa = 240542
  por_vac_pri_dose = (vac_pri_dose / pop_aqa) * 100
  por_vac_seg_dose = (vac_seg_dose / pop_aqa) * 100
  por_vac_ter_dose = (vac_ter_dose / pop_aqa) * 100
  por_vac_qua_dose = (vac_qua_dose / pop_aqa) * 100

  # criação das variáveis de emojis
  emoji_injecao = '💉'
  emoji_sol = '🌇'

  texto_vacina = (f"""
Vacinação em Araraquara {emoji_injecao}{emoji_sol}

Dados do dia: {data_1d.strftime('%d/%m/%Y')}

Total de doses aplicadas:

• 1ª dose: {'{0:,}'.format(vac_pri_dose).replace(',','.')} doses
(Corresponde a {'{0:,}'.format(round(por_vac_pri_dose, 2)).replace('.',',')}% da população)

• 2ª dose: {'{0:,}'.format(vac_seg_dose).replace(',','.')} doses¹
(Corresponde a {'{0:,}'.format(round(por_vac_seg_dose, 2)).replace('.',',')}% da população)

• 3ª dose: {'{0:,}'.format(vac_ter_dose).replace(',','.')} doses
(Corresponde a {'{0:,}'.format(round(por_vac_ter_dose, 2)).replace('.',',')}% da população)

• 4ª dose: {'{0:,}'.format(vac_qua_dose).replace(',','.')} doses
(Corresponde a {'{0:,}'.format(round(por_vac_qua_dose, 2)).replace('.',',')}% da população)

¹ Segunda dose ou dose única.

* População estimada em {'{0:,}'.format(240542).replace(',','.')} pessoas em 2021, de acordo com o IBGE.

* Dados das últimas 24 horas.

       """)
  
  bot.send_message(mensagem.chat.id,texto_vacina)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["drs3"])
def drs3(mensagem):

  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_drs3")

  # Dataframe aba "diário"
  dados_drs3 = planilha.worksheet("dados_drs3")
  dados_drs3 = dados_drs3.get_all_records()
  dfdrs03 = pd.DataFrame(dados_drs3)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS

  # código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # mudança da coluna datahora para o formato de data
  dfdrs03['datahora'] = pd.to_datetime(dfdrs03['datahora'])
 
  # criação variável
  emoji_hospital = '🏥'
  
  data_d1 = dfdrs03['datahora'].iloc[-1]
  ocupacao_leitos_uti = float(dfdrs03['ocupacao_leitos'].iloc[-1])
  ocupacao_leitos_enf = (float(dfdrs03['pacientes_enf_mm7d'].iloc[-1]) / float(dfdrs03['total_covid_enf_mm7d'].iloc[-1])) * 100
  internacoes_uti = float(dfdrs03['pacientes_uti_mm7d'].iloc[-1])
  internacoes_enf = float(dfdrs03['pacientes_enf_mm7d'].iloc[-1])

  texto_drs3 = (f"""
Boletim do dia: {data_d1.strftime('%d/%m/%Y')}

DRS 3 - Araraquara:

Ocupação de leitos¹ {emoji_hospital}

UTI: {'{0:,}'.format(round(ocupacao_leitos_uti, 2)).replace('.',',')}%
Enfermaria: {'{0:,}'.format(round(ocupacao_leitos_enf, 2)).replace('.',',')}%

Internações¹ {emoji_hospital}

UTI: {'{0:,}'.format(round(internacoes_uti, 2)).replace('.',',')}
Enfermaria: {'{0:,}'.format(round(internacoes_enf, 2)).replace('.',',')}

¹ Média móvel 7 dias
         """)
    
  bot.send_message(mensagem.chat.id,texto_drs3)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["leitosdrs"])
def leitosdrs(mensagem):

  bot.send_message(mensagem.chat.id, f"Um instante, gerando o gráfico...")
  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_drs3")

  # Dataframe aba "diário"
  dados_drs3 = planilha.worksheet("dados_drs3")
  dados_drs3 = dados_drs3.get_all_records()
  dfdrs03 = pd.DataFrame(dados_drs3)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS

  #código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

   # Conversão da coluna para o formato da data
  dfdrs03['datahora'] = pd.to_datetime(dfdrs03['datahora'])

  lista_ocupacao_leitos_enf = []
  ienf = 0
  itenf = 0
  size = len(dfdrs03)

  for item in range(size):
    oc_enf = (dfdrs03['pacientes_enf_mm7d'].iloc[ienf]) / (dfdrs03['total_covid_enf_mm7d'].iloc[itenf]) * 100
    lista_ocupacao_leitos_enf.append(oc_enf)
    ienf = ienf + 1
    itenf = itenf + 1  

  dfdrs03['ocupacao_leitos_enf'] = lista_ocupacao_leitos_enf

  x = dfdrs03['datahora']
  y = dfdrs03['ocupacao_leitos']
  z = dfdrs03['ocupacao_leitos_enf']

  fig, ax = plt.subplots(figsize=(12,5))
  line1, = ax.plot(x, y, color = "green", label='Leitos UTI')
  line2, = ax.plot(x, z, color = "blue", label='Leitos Enfermaria')

  ax.set_title("Média móvel - Taxa de Ocupação | DRS 3 Araraquara", fontsize=14, pad=20)
  plt.ylabel('Taxa de Ocupação de Leitos')

  ax.legend()
  fig.autofmt_xdate()
  
  # exportando e importando a imagem
  plt.savefig('/home/mroque/projetos/bots/bot-covid-telegram/imgs/ocupacao_leitos_drs3.png', format='png')
  img_ocupacao_leitos_drs3 = Image.open('/home/mroque/projetos/bots/bot-covid-telegram/imgs/ocupacao_leitos_drs3.png')

  bot.send_message(mensagem.chat.id, f"Pronto, segue gráfico com a evolução da taxa de ocupação de leitos hospitalares na DRS-3 Araraquara:")
  bot.send_photo(mensagem.chat.id, img_ocupacao_leitos_drs3)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)


@bot.message_handler(commands=["internacoes"])
def internacoes(mensagem):

  bot.send_message(mensagem.chat.id, f"Um instante, gerando o gráfico...")
  # INÍCIO CONEXÃO COM O GOOGLE SHEETS

  scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

  json_file = "credentials.json"

  credentials = service_account.Credentials.from_service_account_file(json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  gc = gspread.authorize(scoped_credentials)

  planilha = gc.open("dados_drs3")

  # Dataframe aba "diário"
  dados_drs3 = planilha.worksheet("dados_drs3")
  dados_drs3 = dados_drs3.get_all_records()
  dfdrs03 = pd.DataFrame(dados_drs3)

  # FIM DA CONEXÃO COM O GOOGLE SHEETS  
 
  # código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # Conversão da coluna para o formato da data
  dfdrs03['datahora'] = pd.to_datetime(dfdrs03['datahora'])

  x = dfdrs03['datahora']
  y = dfdrs03['pacientes_uti_mm7d']
  z = dfdrs03['pacientes_enf_mm7d']

  fig, ax = plt.subplots(figsize=(12,5))
  line1, = ax.plot(x, y, color = "green", label='Internações UTI')
  line2, = ax.plot(x, z, color = "blue", label='Internações Enfermaria')

  ax.set_title("Média móvel - Internações | DRS 3 Araraquara", fontsize=14, pad=20)
  plt.ylabel('Internações')

  ax.legend()
  fig.autofmt_xdate()
  
  # exportando e importando a imagem
  plt.savefig('/home/mroque/projetos/bots/bot-covid-telegram/imgs/internacoes_drs3.png', format='png')
  img_internacoes_drs3 = Image.open('/home/mroque/projetos/bots/bot-covid-telegram/imgs/internacoes_drs3.png')

  bot.send_message(mensagem.chat.id, f"Pronto, segue gráfico com a evolução das internações hospitalares por COVID-19 na DRS-3 Araraquara:")
  bot.send_photo(mensagem.chat.id, img_internacoes_drs3)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["ajuda"])
def ajuda(mensagem):

  # código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # criação da variável para receber o emoji
  emoji_email = '✉️'

  # impressão do texto
  ajuda = (f"""
Em caso de dúvidas ou sugestões, envie um e-mail para:

{emoji_email} chatbotcovid@outlook.com
     """)

  bot.send_message(mensagem.chat.id, ajuda)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["info"])
def info(mensagem):
  
  # código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # importação do arquivo com as informações
  with open("/home/mroque/projetos/bots/bot-covid-telegram/texts/info.txt", "r") as arquivo:
    info = arquivo.read()

  # impressão do texto
  info = (f"""
  {info}
       """)
  
  bot.send_message(mensagem.chat.id, info)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["fontes"])
def fonte(mensagem):

  # código para geração de logs em cada opção.
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # importação do arquivo com as fontes utilizadas
  with open("/home/mroque/projetos/bots/bot-covid-telegram/texts/fontes.txt", "r") as arquivo:
    fontes = arquivo.read()

  fontes = (f"""
{fontes}

       """)

  bot.send_message(mensagem.chat.id,fontes)
  emoji_end = '📴'
  emoji_back = '↩️'
  bot.send_message(mensagem.chat.id, f"""
E agora, o que você deseja fazer?

/menu - {emoji_back} Voltar ao menu
/encerrar - {emoji_end} Encerrar o chat              
               """)

@bot.message_handler(commands=["menu"])
def menu(mensagem):
  # código para geração de logs em cada opção
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # criação das variáveis dos emojis
  emoji_robo = '🤖'
  emoji_seta_baixo = '⬇️'
  emoji_jornal = '📰'
  emoji_grafico = '📊'
  emoji_hospital = '🏥'
  emoji_injecao = '💉'
  emoji_ajuda = '❓'
  emoji_fonte = '📂'
  emoji_notificacao = '🔔'
  emoji_end = '📴'

  # importação do arquivo com as notificações do menu
  with open("/home/mroque/projetos/bots/bot-covid-telegram/texts/notificacoes_menu.txt", "r") as arquivo:
     notificacoes_menu = arquivo.read()

  # texto com o menu principal
  menu = (f"""
O que você gostaria de consultar?

Clique em uma das opções abaixo:

Informações de Araraquara {emoji_seta_baixo}

• /boletim - {emoji_jornal} Boletim do dia 
• /casos - {emoji_grafico} Evolução de casos
• /obitos - {emoji_grafico} Evolução de óbitos
• /leitos -  {emoji_hospital} Ocupação de leitos
• /vacina - {emoji_injecao} Vacinação  

Informações DRS 3 - Araraquara {emoji_seta_baixo}

• /drs3 - {emoji_jornal} Boletim do dia
• /leitosdrs - {emoji_hospital} Ocupação de leitos
• /internacoes - {emoji_grafico} Internações

Precisa de algo mais? {emoji_seta_baixo}

• /ajuda - {emoji_ajuda} Dúvidas
• /info - {emoji_robo} Sobre o chatbot
• /fontes - {emoji_fonte} Fontes dos dados

• /encerrar - {emoji_end} Para encerrar o chat

{emoji_notificacao} Notificações: 

{notificacoes_menu}

""")
  
  bot.send_message(mensagem.chat.id, menu)

@bot.message_handler(commands=["encerrar"])
def encerrar(mensagem):
  
  # código para geração de logs
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # variável para o remoji
  emoji_robo = '🤖'

  # mensagem para o usuário
  bot.send_message(mensagem.chat.id, f'Obrigado, {nome_usuario}! Até mais! {emoji_robo}')

# validar qualquer mensagem enviada que não seja comando
def validar(mensagem):
  return True

# função para resposta de mensagem padrão
@bot.message_handler(func=validar)
def resposta_padrao(mensagem):

  # código para geração de logs
  nome_usuario = mensagem.from_user.first_name
  username = mensagem.from_user.username
  datahora = datetime.datetime.now()
  opcao = mensagem.text
  log = f"""{nome_usuario};{username};{opcao};{datahora.strftime('%d-%m-%Y')};{datahora.strftime('%H:%M:%S')}\n"""
  with open("/home/mroque/projetos/bots/bot-covid-telegram/logs/logs.csv", "a") as arquivo:
    arquivo.write(log)

  # criação das variáveis para os emojis
  emoji_feliz = '😀'
  emoji_robo = '🤖'
  emoji_robo = '🤖'
  emoji_seta_baixo = '⬇️'
  emoji_jornal = '📰'
  emoji_grafico = '📊'
  emoji_hospital = '🏥'
  emoji_injecao = '💉'
  emoji_brasil = '🇧🇷'
  emoji_ajuda = '❓'
  emoji_fonte = '📂'
  emoji_notificacao = '🔔'
  emoji_end = '📴'

  # texto de saudação
  texto_saudacao = (f"""
Olá, {nome_usuario}! {emoji_feliz}
Seja bem-vindo(a)!
                """)
  
  # Importar o arquivo txt das notificações do menu
  with open("/home/mroque/projetos/bots/bot-covid-telegram/texts/notificacoes_menu.txt", "r") as arquivo:
   notificacoes_menu = arquivo.read()

  # texto com o menu principal
  menu = (f"""
O que você gostaria de consultar?

Clique em uma das opções abaixo:

Informações de Araraquara {emoji_seta_baixo}

• /boletim - {emoji_jornal} Boletim do dia 
• /casos - {emoji_grafico} Evolução de casos
• /obitos - {emoji_grafico} Evolução de óbitos
• /leitos -  {emoji_hospital} Ocupação de leitos
• /vacina - {emoji_injecao} Vacinação  

Informações DRS 3 - Araraquara {emoji_seta_baixo}

• /drs3 - {emoji_jornal} Boletim do dia
• /leitosdrs - {emoji_hospital} Ocupação de leitos
• /internacoes - {emoji_grafico} Internações

Precisa de algo mais? {emoji_seta_baixo}

• /ajuda - {emoji_ajuda} Dúvidas
• /info - {emoji_robo} Sobre o chatbot
• /fontes - {emoji_fonte} Fontes dos dados

• /encerrar - {emoji_end} Para encerrar o chat

{emoji_notificacao} Notificações: 

{notificacoes_menu}

      """)
  
  bot.send_message(mensagem.chat.id, texto_saudacao)
  bot.send_message(mensagem.chat.id, menu)

# manter o chatbot ativo
#bot.polling(none_stop=True)
#bot.infinity_polling(True)

while True:
  try:
    bot.polling(none_stop=True)
  except:
    time.sleep(5)

#v2.0.0
#23-07-2022