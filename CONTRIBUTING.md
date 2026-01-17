# Přispívání do NovaSandbox

Děkujeme za zájem o přispívání do NovaSandbox! Tento dokument poskytuje pokyny pro přispívače.

## Jak začít

1. **Fork** projektu na GitHubu
2. **Clone** vašeho fork:
   ```bash
   git clone https://github.com/your-username/novasandbox.git
   cd novasandbox
   ```

3. **Instalace dev prostředí**:
   ```bash
   pip install -e .[dev]
   make install-dev
   ```

4. **Vytvoření feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

## Vývoj

### Code Style

Projekt používá:
- **Black** pro formatování (100 znaků na řádek)
- **isort** pro řazení importů
- **flake8** pro linting
- **mypy** pro type checking

Spuštění všech nástrojů:
```bash
make format lint
```

### Testy

Napište testy pro nové funkcionality:

```bash
# Spuštění testů
make test

# S coverage reportem
make coverage

# Benchmark testy
make test-bench
```

### Dokumentace

- Aktualizujte README.md pro nové funkce
- Přidejte docstrings k funkcím a třídám
- Aktualizujte CHANGELOG.md

## Proces Pull Request

1. **Příprava**:
   ```bash
   # Ensure your code is formatted and linted
   make format lint test
   ```

2. **Push** vašich změn:
   ```bash
   git push origin feature/amazing-feature
   ```

3. **Vytvořte Pull Request** na GitHubu se:
   - Jasným popisem změn
   - Odkazem na související issues
   - Potvrzením, že testy prošly

4. **Code review**: Čekejte na feedback od maintainerů

## Pravidla pro PR

- ✅ Testy musí projít
- ✅ Kód musí být naformátovaný (Black/isort)
- ✅ Bez linting chyb (flake8)
- ✅ Type hints pro nové funkcionalitu
- ✅ Dokumentace/docstrings
- ✅ CHANGELOG.md aktualizován

## Reportování bugů

Vytvořte Issue s:
1. Popisem problému
2. Kroky k reprodukci
3. Očekávaný vs. skutečný výsledek
4. Informace o systému (OS, Python verze, atd.)

## Návrhy funkcionalit

Otevřete Discussion nebo Issue s:
1. Použitím a motivací
2. Návrhem API
3. Příklady kódu

## Otázky?

- Otevřete Discussion na GitHubu
- Kontaktujte maintainers

Děkujeme za přispívání! 🚀
