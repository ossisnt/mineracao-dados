Para executar os scripts, aconselha-se uma versão moderna do Python (3.9.2 ou maior).

```python
pip install -U -r requirements.txt
```

## Scripts

Há um total de quatro scripts, cada qual com a sua própria finalidade:

- **step1_avaliar_bandeiras**: Baixa e lê os arquivos de bandeiras presentes no diretório _flags_ e extrair métricas de cores, entropia e complexidade.
- **step2_coletar_dados**: Faz chamadas em repositórios públicos de informação, coleta e pré-formata dados pré-determinados.
- **step3_mesclar_e_limpar_dados**: Unifica as informações da primeira e segunda etapa e realiza mais uma camada de tratamento de dados para fins de compatibilidade com o formato e ferramenta de estudo.
- **step4_consolidaar_dados**: Realiza a leitura da planilha resultado da terceira etapa e cria uma versão final dos dados. Esta etapa é realizada para tratar colunas multivaloradas, com a finalidade de que todas as colunas possuam valores únicos.


## Como executar os scripts:

Estando na raiz do diretório, execute:

```python
# py, python, python3, dependendo de como o binário está associado ao PATH do seu sistema.

# A primeira etapa é computacionalmente intensiva e poderá levar de vários minutos a horas para finalizar.
python scripts\step1_avaliar_bandeiras.py

# A segunda etapa poderá levar alguns minutos para ser concluída devido a quantidade de requisições necessárias para a coleta de dados.
python scripts\step2_coletar_dados.py

python scripts\step3_mesclar_e_limpar_dados.py
python scripts\step4_consolidar_dados.py
```


# Relação de Atributos

| Atributo                  | Descrição                     |
|---------------------------|-------------------------------|
| alpha_code                | Código ISO-3166-2 de identificação do país, utilizado majoritariamente com chave identificadora na hora da mescla este os datasets.    |
| country or territory      | Nome do país ou território autônomo.|
| zone                      | Localização quadrática do país/região de acordo com o Meridiano de Greenwich e Equador.|
| region                    | Região geográfica em que o país se encontra.|
| subregion                 | Sub-região geográfica         |
| life_expectancy           | Expectativa de vida da população (entre homens e mulheres).|
| fertility_rate            | Taxa de fertilidade.|
| currency                  | Moedas utilizadas no país.|
| languages                 | Idiomas falados.|
| religion                  | Religiões adotadas no país.|
| num_colors                | Quantidade de cores identificadas na bandeira, descartando-se tons com pouca cobertura na região total da bandeira (<2%). Estabeleceu-se esta regra pala eliminar a ocorrência de borrões, contornos ou detalhes pequenos e pouco perceptíveis.|
| predominant_color_name    | Cor predominante na bandeira.|
| secondary_color           | Cor secundária da bandeira.|
| color_names               | Nomes das cores identificadas na bandeira.|

*Observações*: Durante a análise, é possível que o algoritmo tenha ignorado ou identificado alguma cor, a depender da complexidade da imagem e sua condição, não avaliamos isto com um problema, visto que esta etapa foi realizada com a intenção de produzir dados para o objeto de estudo de mineração de dados e utilização da ferramenta WEKA.