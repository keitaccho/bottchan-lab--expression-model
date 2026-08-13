# 早見表

コピペして使うもの一覧。

---

## 目次

- [コマンド](#コマンド)
  - [環境確認](#環境確認)
  - [仮想環境](#仮想環境)
  - [Git](#git)
  - [ショートカット](#ショートカット)
- [コードのテンプレート](#コードのテンプレート)
  - [ファイル冒頭](#ファイル冒頭)
  - [src からの呼び出し](#src-からの呼び出し)
  - [図の保存](#図の保存)
  - [ODE を解く](#ode-を解く)
  - [パラメータフィッティング](#パラメータフィッティング)
  - [感度分析](#感度分析)
  - [データの読み書き](#データの読み書き)
  - [よく使う関数](#よく使う関数)
- [文書のテンプレート](#文書のテンプレート)

---

# コマンド


## 環境確認

```bash
pip -V          # どの環境の pip か（.venv が含まれていればOK）
pip list        # 入っているライブラリ
python -V       # Python のバージョン
pwd             # 現在地
```

## 仮想環境

```powershell
.\.venv\Scripts\Activate.ps1        # 有効化（PowerShell）
```

```bash
source .venv/bin/activate            # 有効化（Linux / WSL）
```

```bash
python -m pip install パッケージ名     # インストール
pip freeze > requirements.txt        # 記録
pip install -r requirements.txt      # 復元
```

**基本セット**

```bash
python -m pip install numpy scipy matplotlib pandas ipykernel
```

**モデリング追加**

```bash
python -m pip install lmfit SALib sympy seaborn
```

## Git

```bash
git status              # 変更されたファイル
git pull                # 取り込む（作業開始時）
git add .               # 全部ステージング
git commit -m "内容"     # コミット
git push                # 送信
git log --oneline       # 履歴
```

**初回だけ**

```bash
git config --global user.name "名前"
git config --global user.email "メール"
```

**管理から外す（ファイルは残る）**

```bash
git rm --cached ファイル名
git rm -r --cached フォルダ名/
```

## ショートカット

| キー | 動作 |
|---|---|
| `Ctrl+Shift+P` | コマンドパレット |
| `Ctrl+@` | ターミナル |
| `Ctrl+Shift+G` | ソース管理 |
| `Shift+Enter` | セル実行 |
| `Ctrl+Shift+V` | Markdown プレビュー |

**コマンドパレットで打つもの**

```
Python: Select Interpreter          インタープリタ選択
Notebook: Select Notebook Kernel    カーネル選択
Jupyter: Restart Kernel             カーネル再起動
Developer: Reload Window            リロード
```

---

# コードのテンプレート

## ファイル冒頭

```python
# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import solve_ivp
from pathlib import Path

# 図の共通設定
plt.rcParams['font.size'] = 12
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# パス
ROOT = Path(__file__).parent.parent    # プロジェクトのルート
DATA = ROOT / 'data'
FIG = ROOT / 'figures'
```

`Path` を使うと Windows と Linux の両方で動く。`/` で繋げられる。

```python
FIG / 'fig01.png'      # figures/fig01.png
DATA / 'raw' / 'x.csv' # data/raw/x.csv
```
# ファイル冒頭で1回定義
ROOT = Path(__file__).parent.parent
DATA = ROOT / 'data'
FIG = ROOT / 'figures'

# 以降、短く書ける
df = pd.read_csv(DATA / 'raw' / 'timecourse.csv')
fig.savefig(FIG / 'fig01.png', dpi=300, bbox_inches='tight')

## src からの呼び出し

**notebooks や analysis.py から src の関数を使う**

```python
# %%
import sys
sys.path.append('../src')

from model import simulate, hill
```

**より確実な書き方（どこから実行しても動く）**

```python
# %%
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from model import simulate
```

**src 側の書き方**

```python
# src/model.py

def hill(x, K, n):
    """ヒル関数

    Parameters
    ----------
    x : float or array
        入力濃度
    K : float
        半飽和定数
    n : float
        ヒル係数

    Returns
    -------
    float or array
        0〜1 の値
    """
    return x**n / (K**n + x**n)


def simulate(params, t_span=(0, 100), y0=None):
    """モデルを解く"""
    ...
    return t, y
```

**編集が反映されないとき**（Jupyter は import 済みモジュールをキャッシュする）

```python
# %%
%load_ext autoreload
%autoreload 2
```

冒頭に1回書いておくと、src を編集するたび自動で読み直される。

## 図の保存

**基本形**

```python
fig, ax = plt.subplots(figsize=(6, 4))

ax.plot(t, y, linewidth=2)
ax.set_xlabel('Time (min)')
ax.set_ylabel('Concentration (μM)')

fig.savefig(FIG / 'fig01.png', dpi=300, bbox_inches='tight')
plt.show()
```

**savefig は show より前に書く。**

**複数の線**

```python
fig, ax = plt.subplots(figsize=(6, 4))

for k in [0.1, 0.5, 1.0]:
    t, y = simulate(k)
    ax.plot(t, y, label=f'k = {k}')

ax.set_xlabel('Time (min)')
ax.set_ylabel('Concentration (μM)')
ax.legend()

fig.savefig(FIG / 'fig02.png', dpi=300, bbox_inches='tight')
plt.show()
```

**並べる**

```python
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

axes[0].plot(t, y1)
axes[0].set_title('(a) mRNA')
axes[0].set_xlabel('Time (min)')

axes[1].plot(t, y2)
axes[1].set_title('(b) Protein')
axes[1].set_xlabel('Time (min)')

fig.tight_layout()
fig.savefig(FIG / 'fig03.png', dpi=300, bbox_inches='tight')
plt.show()
```

`2, 2` にすれば 2×2。`axes[0, 1]` で指定する。

**対数軸**

```python
ax.set_xscale('log')
ax.set_yscale('log')
```

**軸の範囲**

```python
ax.set_xlim(0, 100)
ax.set_ylim(0, None)     # 下限だけ指定
```

**保存オプション**

| 書き方 | 意味 |
|---|---|
| `dpi=300` | 解像度。印刷用は300以上 |
| `bbox_inches='tight'` | ラベルが切れないよう調整 |
| `.png` | wiki、スライド用 |
| `.pdf` `.svg` | 論文用、拡大しても劣化しない |

## ODE を解く

**基本形**

```python
from scipy.integrate import solve_ivp

def model(t, y, k1, k2):
    """
    y[0] : mRNA
    y[1] : タンパク質
    """
    mrna, prot = y
    d_mrna = k1 - 0.1 * mrna
    d_prot = k2 * mrna - 0.05 * prot
    return [d_mrna, d_prot]


sol = solve_ivp(
    model,
    t_span=(0, 100),
    y0=[0, 0],
    args=(1.0, 0.5),        # k1, k2
    dense_output=True,
    method='LSODA',
)

t = np.linspace(0, 100, 500)
y = sol.sol(t)

plt.plot(t, y[0], label='mRNA')
plt.plot(t, y[1], label='Protein')
plt.legend()
```

**`dense_output=True`** にすると、任意の時刻の値を `sol.sol(t)` で取れる。滑らかな曲線が描ける。

**method の選び方**

| method | 使う場面 |
|---|---|
| `RK45`（既定） | 普通の系 |
| `LSODA` | 硬い系かどうか自動判定。**迷ったらこれ** |
| `BDF` | 硬い系（時間スケールが大きく異なる） |

計算が異常に遅い、または発散する場合は硬い系の可能性があるので `LSODA` か `BDF` を試す。

**定常状態を求める**

```python
from scipy.optimize import fsolve

def steady_state_eq(y, k1, k2):
    return model(0, y, k1, k2)

y_ss = fsolve(steady_state_eq, x0=[1, 1], args=(1.0, 0.5))
```

**パラメータを振る**

```python
results = {}
for k in [0.1, 0.5, 1.0, 2.0]:
    sol = solve_ivp(model, (0, 100), [0, 0], args=(k, 0.5), dense_output=True)
    results[k] = sol.sol(t)

for k, y in results.items():
    plt.plot(t, y[1], label=f'k1 = {k}')
plt.legend()
```

## パラメータフィッティング

**scipy で**

```python
from scipy.optimize import curve_fit

def hill_model(x, Vmax, K, n):
    return Vmax * x**n / (K**n + x**n)

popt, pcov = curve_fit(hill_model, x_data, y_data, p0=[100, 1, 2])
perr = np.sqrt(np.diag(pcov))     # 標準誤差

print(f'Vmax = {popt[0]:.2f} ± {perr[0]:.2f}')
print(f'K    = {popt[1]:.2f} ± {perr[1]:.2f}')
print(f'n    = {popt[2]:.2f} ± {perr[2]:.2f}')
```

**lmfit で（境界や固定が指定しやすい）**

```python
from lmfit import Model

model = Model(hill_model)
params = model.make_params(Vmax=100, K=1, n=2)

params['n'].min = 0.5          # 下限
params['n'].max = 4            # 上限
params['Vmax'].vary = False    # 固定する

result = model.fit(y_data, params, x=x_data)
print(result.fit_report())

plt.plot(x_data, y_data, 'o', label='data')
plt.plot(x_data, result.best_fit, '-', label='fit')
plt.legend()
```

**決定係数 R²**

```python
def r_squared(y_obs, y_pred):
    ss_res = np.sum((y_obs - y_pred)**2)
    ss_tot = np.sum((y_obs - np.mean(y_obs))**2)
    return 1 - ss_res / ss_tot

print(f'R² = {r_squared(y_data, result.best_fit):.3f}')
```

## 感度分析

**LHS-PRCC（SALib）**

```python
from SALib.sample import latin
from SALib.analyze import rbd_fast
import numpy as np

# パラメータの範囲を定義
problem = {
    'num_vars': 4,
    'names': ['k1', 'k2', 'Kd', 'n'],
    'bounds': [
        [0.1, 10],      # k1
        [0.01, 1],      # k2
        [0.1, 100],     # Kd
        [1, 4],         # n
    ]
}

# サンプリング
param_values = latin.sample(problem, 1000)

# 各パラメータセットでモデルを実行
Y = np.zeros(param_values.shape[0])
for i, params in enumerate(param_values):
    Y[i] = run_model(*params)     # 出力を1つの値にする

# 感度を計算
Si = rbd_fast.analyze(problem, param_values, Y)
print(Si)
```

**PRCC を自前で計算**

```python
from scipy.stats import rankdata
import numpy as np

def prcc(X, y):
    """偏順位相関係数

    X : (n_samples, n_params)
    y : (n_samples,)
    """
    Xr = np.apply_along_axis(rankdata, 0, X)
    yr = rankdata(y)

    n_params = X.shape[1]
    result = np.zeros(n_params)

    for i in range(n_params):
        others = np.delete(Xr, i, axis=1)
        others = np.column_stack([np.ones(len(yr)), others])

        # 他のパラメータで回帰した残差
        res_x = Xr[:, i] - others @ np.linalg.lstsq(others, Xr[:, i], rcond=None)[0]
        res_y = yr - others @ np.linalg.lstsq(others, yr, rcond=None)[0]

        result[i] = np.corrcoef(res_x, res_y)[0, 1]

    return result
```

**結果の可視化**

```python
names = problem['names']
values = prcc(param_values, Y)

fig, ax = plt.subplots(figsize=(6, 4))
colors = ['tab:red' if v > 0 else 'tab:blue' for v in values]
ax.barh(names, values, color=colors)
ax.axvline(0, color='k', linewidth=0.8)
ax.set_xlabel('PRCC')
fig.savefig(FIG / 'sensitivity.png', dpi=300, bbox_inches='tight')
```

## データの読み書き

```python
import pandas as pd

# 読む
df = pd.read_csv(DATA / 'raw' / 'timecourse.csv')
df = pd.read_excel(DATA / 'raw' / 'data.xlsx', sheet_name='Sheet1')

# 見る
df.head()           # 先頭5行
df.info()           # 列の型と欠損
df.describe()       # 統計量
df.columns          # 列名

# 選ぶ
df['time']                      # 1列
df[['time', 'gfp']]             # 複数列
df[df['iptg'] > 0.5]            # 条件で行を選ぶ

# 書く
df.to_csv(DATA / 'processed' / 'cleaned.csv', index=False)

# numpy 配列に変換
t = df['time'].values
y = df['gfp'].values
```

**グループごとに処理**

```python
for iptg, group in df.groupby('iptg'):
    plt.plot(group['time'], group['gfp'], label=f'{iptg} mM')
plt.legend()
```

**結果を保存**

```python
results = pd.DataFrame({
    'time': t,
    'mrna': y[0],
    'protein': y[1],
})
results.to_csv(DATA / 'processed' / 'simulation.csv', index=False)
```

## よく使う関数

```python
# 等間隔の配列
np.linspace(0, 100, 500)        # 0から100を500分割
np.logspace(-2, 2, 50)          # 10^-2 から 10^2 を対数等間隔

# 統計
np.mean(x), np.std(x), np.median(x)
np.min(x), np.max(x)

# 配列操作
np.array([1, 2, 3])
np.zeros(10), np.ones(10)
np.column_stack([a, b])          # 列方向に結合

# 保存・読み込み
np.save('data.npy', arr)
arr = np.load('data.npy')
```

---

# 文書のテンプレート

## README.md

```markdown
# プロジェクト名

一行の説明。

## 環境構築

\`\`\`bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
\`\`\`

## 構成

- `src/` : モデルのコード
- `notebooks/` : 探索・解析
- `notes/` : メモ、考察
- `data/raw/` : 生データ（変更しない）
- `data/processed/` : 加工後
- `figures/` : 図

## 使い方

\`\`\`bash
python src/model.py
\`\`\`
```

## 作業ログ（notes/YYYY-MM-DD.md）

```markdown
# 2026-08-13

## やったこと
-

## わかったこと
-

## 疑問
-

## 次にやること
- [ ]
- [ ]
```

## 図の記録（figures/README.md）

```markdown
# 図の一覧

## fig01_dynamics.png
IPTG濃度を変えたときの発現量の時間変化

- 生成: `src/model.py` の `plot_dynamics()`
- データ: `data/processed/timecourse.csv`
- パラメータ: k1=1.0, k2=0.5
- 作成日: 2026-08-13
```

## .gitignore

```
# Python
__pycache__/
*.pyc
.ipynb_checkpoints/
venv/
.venv/

# データ
data/raw/*.csv
*.h5

# OS
.DS_Store
Thumbs.db

# 一時ファイル
*.tmp
*.log
```

## Ruff の設定（settings.json）

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  }
}
```

**整形させたくない箇所**

```python
# fmt: off
A = np.array([
    [1, 0, 0],
    [0, 1, 0],
])
# fmt: on
```

---

# 新規プロジェクトの立ち上げ

```bash
git clone <URL>
cd <リポジトリ名>
code .
```

```
Ctrl+Shift+P → Python: Create Environment → venv
```

ターミナルを開き直して、

```bash
pip -V                                              # .venv か確認
python -m pip install numpy scipy matplotlib pandas ipykernel
pip freeze > requirements.txt
mkdir notes src notebooks figures data
mkdir data\raw data\processed
```

`.gitignore` と `README.md` を作ってから、

```bash
git add .
git commit -m "初期構成"
git push
```
