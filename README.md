Para executar os scripts, aconselha-se uma versão moderna do Python (3.9.2 ou maior).

```python
pip install -U -r requirements.txt
```

## Scripts

Há um total de quatro scripts, cada qual com a sua própria finalidade:

- **step1_avaliar_bandeiras**: Baixa e lê os arquivos de bandeiras presentes no diretório _flags_ e extrai composição de cores, entre primaria e secundaria, tal como, eliminando cores pouco significativas.
- **step2_coletar_dados**: Faz chamadas em repositórios públicos de informação, coleta e pré-formata dados pré-determinados.
- **step3_mesclar_e_limpar_dados**: Unifica as informações da primeira e segunda etapa e realiza mais uma camada de tratamento de dados para fins de compatibilidade com o formato e ferramenta de estudo.
- **step4_consolidaar_dados**: Realiza a leitura da planilha resultado da terceira etapa e cria uma versão final dos dados. Esta etapa é realizada para tratar colunas multivaloradas, com a finalidade de que todas as colunas possuam valores únicos, por ocasião, também são adicionadas novas colunas para complemento de informações.


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
| alpha_code                | Código ISO-3166-2 de identificação do país, utilizado majoritariamente com chave identificadora na hora da mescla este o conjunto de dados.    |
| country or territory      | Nome do país ou território autônomo.|
| zone                      | Localização quadrática do país/região de acordo com o Meridiano de Greenwich ou Equador.|
| region                    | Região geográfica em que o país se encontra.|
| subregion                 | Sub-região geográfica         |
| life_expectancy           | Expectativa de vida da população (entre homens e mulheres) arredondado em múltiplos de 5.|
| fertility_rate            | Taxa de fertilidade, sem considerar valores decimais (apenas valores inteiros).|
| num_colors                | Quantidade de cores identificadas na bandeira, descartando-se tons com pouca cobertura na região total da bandeira (<2%). Estabeleceu-se esta regra pala eliminar a ocorrência de borrões, contornos ou detalhes pequenos e pouco perceptíveis.|
| primary_color             | Cor predominante na bandeira.|
| secondary_color           | Cor secundária da bandeira.|
| most_ranked_color         | Cor melhor posicionada entre todo o conjunto de cores identificado na análise e presente na instância.|
| currency_primary          | Moeda principal utilizada no país.|
| currency_secondary        | Moeda secundaria utilizada no país.|
| languages_primary         | Idioma principal falado no país.|
| languages_secondary       | Idioma secundário falado no país.|
| religion_primary          | Religião principal adotada no país.|
| religion_secondary        | Religião secundária adotada no país.|
| pop2023                   | População em 2023.|
| density                   | Densidade populacional.
| hdiTier                   | Nível de IDH.|
| area                      | Área ocupada pelo País ou Território.|
| landAreaKm                | Área ocupada pelo País ou Território em quilômetros.|
| growthRate                | Taxa de crescimento populacional.|
| hdi2021                   | IDH em 2021.|
| densityMi                 | Densidade por milhão.|
| country_or_territory_status | Classe de estudo com indicativo se o País é Desenvolvido ou esta em Desenvolvimento.|


*Observações*: Durante a análise, é possível que o algoritmo tenha ignorado ou identificado alguma cor, a depender da complexidade da imagem e sua condição, não avaliamos isto com um problema, visto que esta etapa foi realizada com a intenção de produzir dados para o objeto de estudo de mineração de dados e utilização da ferramenta WEKA.

Para os campos *languages*, *religion* e *currency*, as informações foram coletadas pela internet, onde nem todas os países ou regiões autônomas possuem tal informação a disposição por meio das APIs ou páginas públicas. Devido a natureza das informações, algumas desses campos são multivalorados, aonde estão, tivemos a seguinte abordagem de tratamento:

- Nos campos definidos como *primary*, utilizou-se o primeiro valor do conjunto de dados, assumindo-se que este possa ser a moeda, religião ou idioma principal do país ou região, no entanto, existe a possibilidade disto não ser completamente representativo à realidade, dado não termos controle sobre esta entrada de dados e o seu preenchimento.
- Nos campos definidos como *secondary*, atribui-se um peso ao conjunto de valores únicos como um todo e avalia-se individualmente cada instância, onde então, para o valor secundário, atribui-se o valor mais importante entre os existentes, excluindo-se o primeiro valor já presente no campo *primary*.
- Campos vazios, nulos ou com valores indefinidos, foram classificados com o valor "Other".
- Para *fertility_rate* e *life_expectancy*, valores inválidos, nulos ou não presentes, foram preenchidos com 0.
