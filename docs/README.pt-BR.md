<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ModelScope Daily

**Script de arquivo único para o check-in diário do ModelScope CN e Internacional, com tokens separados, verificação do livro de créditos, leitura de saldo e uso.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> A documentação completa em chinês está em [../README.md](../README.md).

## ✨ Recursos principais

- Mantém credenciais CN e Internacionais separadas.
- Dispara o check-in diário via `GET /api/v1/users/login/info`.
- Confirma créditos CN pelo endpoint `/openapi/v1/magicubes/transactions`.
- Agrega ganhos `daily_active` e `aliyun_bindlogin` do mesmo dia.
- Consulta créditos totais, disponíveis, congelados e o uso de inferência do dia.
- Compatível com envelopes de resposta em maiúsculas e minúsculas.
- Diferencia HTTP `401` de autenticação e HTTP `403` de controle de risco.

## 🧭 Como funciona

O ModelScope não possui um botão de check-in separado. A chamada ao endpoint de informações de login dispara o check-in diário e chamadas repetidas são idempotentes.

```text
token ms-
  → Cookie: m_session_id=<token>
  → GET /api/v1/users/login/info
  → CN: verifica o livro de créditos do dia
  → lê saldo e uso
  → reporta confirmado / já recebido / não confirmado / falha
```

`--query` também chama o endpoint e, portanto, dispara o check-in. Não existe modo totalmente somente leitura.

## 🚀 Configuração mínima

```bash
python -m pip install -r requirements.txt
```

Crie um token `ms-` no console correspondente do ModelScope.

Conta única:

```text
MODELSCOPE_CN_TOKEN=ms-CN_TOKEN
MODELSCOPE_INTL_TOKEN=ms-INTL_TOKEN
```

Várias contas:

```text
MODELSCOPE_CN_TOKENS=
CN Principal|ms-CN_TOKEN
CN Secundária|ms-CN_TOKEN

MODELSCOPE_INTL_TOKENS=
Intl Principal|ms-INTL_TOKEN
```

Execução:

```bash
python modelscope_daily.py
python modelscope_daily.py --only 1
python modelscope_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

Defina `MODELSCOPE_CN_TOKENS` e/ou `MODELSCOPE_INTL_TOKENS` e crie:

```text
30 8 * * * python3 modelscope_daily.py
```

Use `--only` na primeira validação para inspecionar cada token separadamente.

## ☁️ GitHub Actions

O workflow está em [../.github/workflows/daily.yml](../.github/workflows/daily.yml). A execução manual está ativa e o agendamento vem comentado.

| Secret | Obrigatório | Uso |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | Um dos dois | Tokens CN de várias contas |
| `MODELSCOPE_INTL_TOKENS` | Um dos dois | Tokens internacionais de várias contas |
| `MODELSCOPE_CN_TOKEN` | Um dos dois | Token CN de uma conta |
| `MODELSCOPE_INTL_TOKEN` | Um dos dois | Token internacional de uma conta |
| `MODELSCOPE_PROXY` | Opcional | Proxy |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | Opcional | Notificações |

Para ativar o agendamento, remova os comentários. `30 0 * * *` usa UTC e corresponde a 08:30 em Pequim.

## 🔧 Variáveis principais

| Variável | Descrição |
| :--- | :--- |
| `MODELSCOPE_CN_TOKENS` | Várias contas CN: `nome\|ms-token` |
| `MODELSCOPE_INTL_TOKENS` | Várias contas internacionais: `nome\|ms-token` |
| `MODELSCOPE_CN_TOKEN` | Conta CN única |
| `MODELSCOPE_INTL_TOKEN` | Conta internacional única |
| `MODELSCOPE_PROXY` | Proxy HTTP(S) / SOCKS |
| `MODELSCOPE_VERIFY_DELAY` | Espera antes de reler o livro CN; padrão `2` segundos |
| `MODELSCOPE_NO_NOTIFY` | `1` desativa notificações |

## 📊 Critério de sucesso

| Caso | Resultado |
| :--- | :--- |
| HTTP `401` | Token inválido ou usado no site errado |
| HTTP `403` | Bloqueio de risco, não necessariamente login expirado |
| Balance ausente | Falha de consulta, nunca exibida como saldo zero |
| Livro CN | Precisa conter `type=EARN` do dia com `daily_active` ou `aliyun_bindlogin` |
| Livro CN inicialmente vazio | Repetir uma vez após `MODELSCOPE_VERIFY_DELAY` |
| Site internacional | Sem API de botão separada; reporta pela ocorrência do login |

Sem um lançamento válido no livro CN, a conta é reportada como não confirmada.

## 📦 Informações da versão

A versão atual é `v1.0.2`. Ela separa `401` e `403` e falha em vez de mostrar saldo zero quando o envelope está incompleto. O CHANGELOG registra sete novos testes offline e onze testes aprovados no total. Também informa que essa rodada não usou conta real nem enviou check-ins reais.

## 🔒 Privacidade

- O projeto não coleta nem envia dados da conta.
- Os logs não exibem o token `ms-` completo.
- Não envie `.env` ou logs ao Git.
- Guarde tokens apenas em variáveis locais, GitHub Secrets ou variáveis do Qinglong.
- Remova tokens, apelidos, IDs e detalhes do livro antes de abrir uma issue.

## Limites de uso e redistribuição

O repositório oficial, os scripts, as instruções de implantação e os downloads das Releases são gratuitos. Não são permitidos empacotamento pago, implantação paga, exigência de assinatura, revenda, remoção de autoria, personificação do autor, uso da identidade ou dos QR codes do autor como endosso, nem repostagem em contas, grupos ou canais sem relação para desviar tráfego. O conteúdo irregular pode ser retirado; o autor pode pausar atualizações, arquivar ou excluir o repositório. Consulte [../NOTICE.md](../NOTICE.md) para as regras completas.

## 🔗 Links

- [Releases](https://github.com/L0NE-6/ModelScope-Daily/releases)
- [Issues](https://github.com/L0NE-6/ModelScope-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
