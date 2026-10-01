# agi

## Secrets

AWS access goes through the SSO profile `private` (`aws sso login --profile private`);
no static AWS keys are used. API keys are read from the environment when set, otherwise
from SSM Parameter Store SecureString parameters in that account
(`aws_private.secret`):

| Env var | Parameter |
|---------|-----------|
| `OPENAI_API_KEY` | `/secrets/agi/openai-api-key` |
| `API_KEY` | `/secrets/agi/twitter-api-key` |
| `API_KEY_SECRET` | `/secrets/agi/twitter-api-key-secret` |
| `ACCESS_TOKEN` | `/secrets/agi/twitter-access-token` |
| `ACCESS_TOKEN_SECRET` | `/secrets/agi/twitter-access-token-secret` |
| `BEARER_TOKEN` | `/secrets/agi/twitter-bearer-token` |
