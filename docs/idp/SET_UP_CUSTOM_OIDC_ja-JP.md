# 外部アイデンティティプロバイダの設定

## ステップ 1: OIDCクライアントの作成

対象のOIDCプロバイダーの手順に従い、OIDCクライアントIDとシークレットの値を記録してください。また、次のステップで発行者URLが必要になります。セットアップ過程でリダイレクトURIが必要な場合は、デプロイ完了後に置き換えられるダミー値を入力してください。

## ステップ 2: AWS Secrets Managerに認証情報を保存する

1. AWS Management Consoleにアクセスします。
2. Secrets Managerに移動し、「新しいシークレットを保存」を選択します。
3. 「その他のタイプのシークレット」を選択します。
4. クライアントIDとクライアントシークレットをキーと値のペアで入力します。

   - キー: `clientId`、値: <YOUR_GOOGLE_CLIENT_ID>
   - キー: `clientSecret`、値: <YOUR_GOOGLE_CLIENT_SECRET>
   - キー: `issuerUrl`、値: <ISSUER_URL_OF_THE_PROVIDER>

5. プロンプトに従ってシークレットに名前と説明を付けます。CDKコードで使用するため、シークレット名をメモしておきます（ステップ 3の変数名 <YOUR_SECRET_NAME>で使用）。
6. シークレットを確認して保存します。

### 注意

キー名は、文字列 `clientId`、`clientSecret`、`issuerUrl` と完全に一致する必要があります。

## ステップ 3: cdk.json の更新

cdk.json ファイルに ID プロバイダと SecretName を追加します。

以下のようになります：

```json
{
  "context": {
    // ...
    "identityProviders": [
      {
        "service": "oidc", // 変更しないでください
        "serviceName": "<YOUR_SERVICE_NAME>", // 好きな値を設定してください
        "secretName": "<YOUR_SECRET_NAME>"
      }
    ],
    "userPoolDomainPrefix": "<UNIQUE_DOMAIN_PREFIX_FOR_YOUR_USER_POOL>"
  }
}
```

### 注意

#### 一意性

`userPoolDomainPrefix` は、すべての Amazon Cognito ユーザー間でグローバルに一意である必要があります。すでに他の AWS アカウントで使用されているプレフィックスを選択すると、ユーザープールドメインの作成に失敗します。一意性を確保するために、識別子、プロジェクト名、または環境名をプレフィックスに含めることをお勧めします。

## ステップ 4: CDKスタックのデプロイ

AWS に CDK スタックをデプロイします：

```sh
npx cdk deploy --require-approval never --all
```

## ステップ 5: Cognito のリダイレクト URI で OIDC クライアントを更新

スタックをデプロイした後、`AuthApprovedRedirectURI` が CloudFormation のアウトプットに表示されます。OIDC 設定に戻り、正しいリダイレクト URI で更新してください。