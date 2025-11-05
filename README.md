# CIDR Optimizer (IPv4) - 日本語 README

このリポジトリは、指定した IPv4 CIDR ブロックから特定の IP アドレスを除外し、残った IP アドレス集合を最小限の CIDR ブロック群に圧縮 (collapse) するシンプルなスクリプトを提供します。

`ipaddress` 標準ライブラリの `collapse_addresses` を利用して、個別の IP を最小限のネットワーク表現にまとめることで、アクセス制限やファイアウォール設定、許可リスト（Allowlist）生成などに役立ちます。

---
## 特長
- 指定 CIDR 内のすべての IP を展開
- 除外したい IPv4 アドレスを任意個指定可能
- 除外後の残差集合を最小数の CIDR ブロックへ圧縮
- 入力値の妥当性検証（不正な IP / CIDR でエラー終了）
- Python 標準ライブラリのみで動作（追加依存なし）

---
## 動作要件
- Python 3.10+（`ipaddress` モジュールは 3.3 以降標準搭載）

---
## 使い方
プロジェクトルートで以下を実行します:

```bash
python src/main.py --source-cidr <CIDR> --exclude <IP1> <IP2> <IP3> ...
```

### 引数説明
| 引数 | 必須 | 説明 |
|------|------|------|
| `--source-cidr` | はい | 対象となる IPv4 CIDR (例: `192.168.0.0/24`) |
| `--exclude` | いいえ | 除外したい IPv4 アドレス（スペース区切りで複数指定可） |

### 例1: いくつかの IP を除外
```bash
python src/main.py --source-cidr 192.168.0.0/29 --exclude 192.168.0.2 192.168.0.3
```
`192.168.0.0/29` は以下 8 個の IP を含みます:
```
192.168.0.0
192.168.0.1
192.168.0.2
192.168.0.3
192.168.0.4
192.168.0.5
192.168.0.6
192.168.0.7
```
上記から `192.168.0.2` と `192.168.0.3` を除外すると残りは 6 個になり、最小の CIDR 群へ圧縮されます。

出力例:
```
##### Result #####
192.168.0.0/31
192.168.0.4/30
192.168.0.6/31
##### End Result #####
```

### 例2: 除外なし
```bash
python src/main.py --source-cidr 10.0.0.0/30
```
出力:
```
##### Result #####
10.0.0.0/30
##### End Result #####
```

### 例3: 除外後ゼロ件
```bash
python src/main.py --source-cidr 10.0.0.0/30 --exclude 10.0.0.0 10.0.0.1 10.0.0.2 10.0.0.3
```
出力:
```
No IPs remain after exclusion. Nothing to collapse.
```

---
## エラーハンドリング
| 状況 | メッセージ例 | 対処 |
|------|--------------|------|
| 不正な CIDR | `Invalid --source-cidr value: ...` | 入力値を修正 |
| 不正な除外 IP | `Invalid IP in --exclude list: ...` | 該当 IP を削除 / 修正 |
| 変換時不正 IP | `Invalid IP address provided: ...` | 入力一覧を再確認 |

---
## 仕組み概要
1. `--source-cidr` を `ipaddress.ip_network(..., strict=False)` で展開
2. `--exclude` リストを `IPv4Address` 型に変換
3. 差集合（除外後 IP）を文字列リスト化
4. `ipv4_address_to_cidr()` で `collapse_addresses` を適用
5. 結果を表示

`collapse_addresses` は連続したアドレス群を最小限の `IPv4Network` リストにまとめます。

---
## 関数概要
### `parse_args()`
CLI 引数パーサを構築し、`Namespace` を返します。

### `main()`
スクリプトのエントリポイント。入力 → フィルタ → 圧縮 → 出力のオーケストレーションを担当。

### `ipv4_address_to_cidr(ip_list)`
与えられた IPv4 アドレス群（文字列または `IPv4Address`）を最小 CIDR 群に圧縮して返却。

---
## 開発者向けメモ
- 依存は標準ライブラリのみ
- 今後の拡張候補:
  - IPv6 対応
  - 除外範囲 (CIDR) のサポート
  - 結果の JSON / CSV 出力
  - ファイル入力サポート

---
## ライセンス
このリポジトリに明示的なライセンスがない場合、私的利用目的での利用を想定しています。公開・商用利用や再配布を行う場合はライセンスを追加してください。

---
## コンタクト
改善案や不具合報告は Issue もしくは Pull Request でお知らせください。

