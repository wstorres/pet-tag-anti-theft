# 🐾 Project Context & Architecture Master: Pet Tag Anti-Theft (SafePet ID)

> **Instrução para LLMs e Assistentes (ex: Gemini 3.8 Flash Low):**  
> Este documento é o mapa de contexto e escopo técnico absoluto deste projeto. Utilize estas diretrizes para qualquer geração de código, refatoração, criação de novos handlers, rotas ou documentação.

---

## 1. Visão Geral do Negócio & Proposta de Valor

- **Nome do Projeto:** SafePet ID (Pet Tag Anti-Theft)
- **Modelo de Negócio:** Hardware OEM (AliExpress/MochuaRFID) + Plataforma Serverless (AWS). Venda direta (B2C) e canal físico B2B2C (displays em papelarias/pet shops) sem mensalidade para o consumidor final.
- **Hardware:** Tags em PVC + Resina Epóxi (NTAG215 - 504 bytes) personalizadas de fábrica com marca na frente e QR Code + ID dinâmico no verso.
- **Diferencial Anti-Apropriação Indébita:** Ao escanear o QR Code/NFC, o sistema executa um processo silencioso de captura de metadados de rede (IP, User-Agent, timestamp e resolução GeoIP), registrando um log de auditoria no banco de dados e notificando imediatamente o tutor via webhook/SMS/WhatsApp.

---

## 2. Arquitetura da Solução (Serverless Zero-Fixed-Cost)

O projeto foi desenhado para operar com **custo fixo mensal de R$ 0,00** na camada de uso da AWS:

[ Celular / Leitor ]
│
▼
[ AWS CloudFront / API Gateway ]
│
▼
[ AWS Lambda (Python 3.11+) ]
├── scan_tag.py (Captura passiva + GeoIP + Alerta)
├── register_pet.py (Vínculo de tag virgem ao pet)
└── get_pet_info.py (Perfil público do pet)
│
├──► [ Amazon DynamoDB (NoSQL) ]
└──► [ Serviço de Notificação (Resend/SNS/Webhook) ]

---

## 3. Modelo de Dados (Amazon DynamoDB)

### Tabela 1: `Pets`
- **Partition Key (`PK`):** `pet_id` (String - UUID ou hash)
- **Atributos:** `tag_id`, `pet_name`, `species`, `breed`, `owner_name`, `owner_phone`, `owner_email`, `medical_notes`, `is_lost` (Boolean), `created_at`.

### Tabela 2: `Tags`
- **Partition Key (`PK`):** `tag_id` (String - ex: `TAG-001`)
- **Atributos:** `status` (`VIRGIN` | `ACTIVE` | `BLOCKED`), `bound_pet_id`, `batch_id`, `created_at`.

### Tabela 3: `AccessLogs` (Inteligência Anti-Apropriação)
- **Partition Key (`PK`):** `tag_id` (String)
- **Sort Key (`SK`):** `timestamp` (String ISO-8601)
- **Atributos:** `ip`, `user_agent`, `city`, `region`, `country`, `isp`, `lat`, `lon`, `alert_sent` (Boolean).

---

## 4. Estrutura de Diretórios do Repositório

```text
pet-tag-anti-theft/
├── PROJECT_CONTEXT.md       # Este arquivo de contexto master
├── requirements.txt         # Dependências Python (boto3, requests, pydantic)
├── backend/
│   ├── handlers/
│   │   ├── scan_tag.py      # Captura de IP, GeoIP, Log e Notificação
│   │   ├── register_pet.py  # Cadastro do pet e ativação da tag
│   │   └── get_pet_info.py  # Exibição do perfil público do animal
│   └── services/
│       ├── geoip_service.py # Integração com serviços de localização por IP
│       └── notify_service.py# Envio de alertas ao tutor
├── frontend/                # WebApp responsivo para leitura e cadastro
├── infrastructure/          # IaC (Serverless Framework / SAM)
└── docs/                    # Manuais funcionais e especificações

5. Diretrizes de Código e Padrões de Manutenção
Eficiência e Latência: Mantenha os arquivos Lambda enxutos. O handler scan_tag.py deve responder em menos de 500ms para garantir que a localização e o log sejam capturados antes do utilizador fechar a página.

Segurança e Privacidade: Nenhum dado pessoal sensível do tutor deve ser exposto publicamente sem consentimento. O perfil público deve exibir apenas o nome do pet, alertas de saúde e botões de contacto direto.

Log de Auditoria: Toda a tentativa de leitura deve gerar obrigatoriamente um registo na tabela AccessLogs

