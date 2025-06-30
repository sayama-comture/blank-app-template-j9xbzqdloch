# Konfiguracja zewnętrznego dostawcy tożsamości

## Krok 1: Utworzenie klienta OIDC

Postępuj zgodnie z procedurami dla docelowego dostawcy OIDC i zanotuj wartości identyfikatora klienta OIDC oraz jego sekretu. Adres URL wystawcy będzie również potrzebny w kolejnych krokach. Jeśli w procesie konfiguracji wymagany jest identyfikator URI przekierowania, wprowadź tymczasową wartość, która zostanie zastąpiona po zakończeniu wdrożenia.

## Krok 2: Przechowywanie poświadczeń w AWS Secrets Manager

1. Przejdź do konsoli zarządzania AWS.
2. Przejdź do Secrets Manager i wybierz "Store a new secret".
3. Wybierz "Other type of secrets".
4. Wprowadź identyfikator klienta i sekret klienta jako pary klucz-wartość.

   - Klucz: `clientId`, Wartość: <YOUR_GOOGLE_CLIENT_ID>
   - Klucz: `clientSecret`, Wartość: <YOUR_GOOGLE_CLIENT_SECRET>
   - Klucz: `issuerUrl`, Wartość: <ISSUER_URL_OF_THE_PROVIDER>

5. Postępuj zgodnie z monitami, aby nazwać i opisać sekret. Zanotuj nazwę sekretu, ponieważ będzie ona potrzebna w kodzie CDK (Użyta w zmiennej kroku 3 <YOUR_SECRET_NAME>).
6. Przejrzyj i zapisz sekret.

### Uwaga

Nazwy kluczy muszą dokładnie odpowiadać ciągom `clientId`, `clientSecret` i `issuerUrl`.

## Krok 3: Aktualizacja pliku cdk.json

W pliku cdk.json dodaj dostawcę tożsamości i nazwę sekretu.

w następujący sposób:

```json
{
  "context": {
    // ...
    "identityProviders": [
      {
        "service": "oidc", // Nie zmieniaj
        "serviceName": "<TWOJA_NAZWA_USŁUGI>", // Ustaw dowolną wartość
        "secretName": "<TWOJA_NAZWA_SEKRETU>"
      }
    ],
    "userPoolDomainPrefix": "<UNIKALNY_PREFIKS_DOMENY_DLA_TWOJEJ_PULI_UŻYTKOWNIKÓW>"
  }
}
```

### Uwaga

#### Unikalność

Prefiks `userPoolDomainPrefix` musi być globalnie unikalny we wszystkich użytkownikach Amazon Cognito. Jeśli wybierzesz prefiks, który jest już używany przez inne konto AWS, utworzenie domeny puli użytkowników zakończy się niepowodzeniem. Dobrą praktyką jest dołączenie identyfikatorów, nazw projektów lub nazw środowisk do prefiksu, aby zapewnić unikalność.

## Krok 4: Wdrożenie stosu CDK

Wdróż swój stos CDK w AWS:

```sh
npx cdk deploy --require-approval never --all
```

## Krok 5: Aktualizacja klienta OIDC za pomocą adresów URL przekierowania Cognito

Po wdrożeniu stosu w danych wyjściowych CloudFormation pojawi się `AuthApprovedRedirectURI`. Wróć do konfiguracji OIDC i zaktualizuj ją o poprawne adresy URL przekierowania.