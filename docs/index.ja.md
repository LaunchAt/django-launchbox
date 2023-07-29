# ホーム

## 概要

Django LaunchBox は、 Django によるバックエンド開発に必要な、基本的なツールとユーティリティを提供する、強力で便利なパッケージです。

## 必要条件

次のバージョンと互換性があります：

* Python: 3.8、3.9、3.10、3.11
* Django: 3.2、4.1、4.2

最高の体験を得るために、 Python と Django シリーズの最新のパッチリリースを強く推奨し、公式にサポートしています。

## インストール

Django LaunchBox は、 `pip` や相当するパッケージ管理ソフトウエアなどからインストールできます：

```sh
pip install git+https://github.com/LaunchAt/django-launchbox.git
```

パッケージをインストールした後は、Djangoプロジェクトの設定で `INSTALLED_APPS` に `'launchbox'` を追加してください：

```python
INSTALLED_APPS = [
    ...
    'launchbox',
]
```

## ライセンス

このパッケージは、 [The 3-Clause BSD License](https://github.com/LaunchAt/django-launchbox/blob/master/LICENSE) の下でリリースされています。

## セキュリティ

セキュリティ目的のため、 `django-launchbox` の最新バージョンのみがアクティブにサポートされています。
脆弱性を発見した場合は、 [develop@launchat.jp](mailto:develop@launchat.jp) までメールで報告してください。

---

貢献や問題の報告は歓迎しています。
是非 Django LaunchBox の開発に参加してください。
Happy coding!
