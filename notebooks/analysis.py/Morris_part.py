# %%
import numpy as np
from scipy.integrate import solve_ivp
from SALib.sample import morris as morris_sample
from SALib.analyze import morris as morris_analyze
import json

# ============================================================
# パラメータ範囲（出典・信頼度は同梱の morris_parameter_table.md 参照）
#   scale: "log"=log10一様サンプリング, "lin"=線形一様サンプリング
# ============================================================
PROBLEM_DEF = {
    # name: (low, high, scale)
    "k_transcript": (0.03, 0.3, "log"),        # nM/s  ← log_k_transrate.txt の値（名称入替に注意）
    "leak_per":     (0.01, 0.05, "lin"),       # 無次元
    "EtO":          (0.01, 100.0, "log"),      # uM（式内で*1e3）
    "dm":           (1.7e-3, 5.8e-3, "log"),   # 1/s
    "k_transrate":  (0.01, 0.17, "log"),       # 1/s   ← log_k_transcript.txt の値（名称入替に注意）
    "k_fold":       (5e-4, 5e-3, "log"),       # 1/s
    "PLP":          (500.0, 2000.0, "log"),    # nM
    "Kd_PLP":       (100.0, 500.0, "log"),     # nM
    "k_tatcat":     (0.005, 0.02, "log"),      # 1/s
    "TatAyCy":      (1.0, 40.0, "log"),        # nM
    "K_tat":        (5.0, 30.0, "log"),        # nM
    "k_on":         (50.0, 5000.0, "log"),     # 1/s
    "k_off":        (0.005, 0.15, "log"),      # 1/s
    "S_Max":        (66.4, 664.0, "log"),      # mM   ※簡易推定（下記参照）
    "d_spread":     (1e-6, 1e-4, "log"),       # 1/s  ※定常期・プロテアーゼなしのベースケース
    "k_deg_u":      (3.9e-4, 5.8e-3, "log"),   # 1/s  ※新規・簡易推定（文献値なし）
}
N_LYSM_FIXED = 3.0   # 固定（k_off レンジがアビディティ効果込みのため独立変数化しない）
T_EVAL = 259200.0    # 72 h
IC = 1e-4             # 全状態の初期値 [nM]

NAMES = list(PROBLEM_DEF.keys())
BOUNDS = []
for n in NAMES:
    lo, hi, sc = PROBLEM_DEF[n]
    if sc == "log":
        BOUNDS.append([np.log10(lo), np.log10(hi)])
    else:
        BOUNDS.append([lo, hi])

problem = {"num_vars": len(NAMES), "names": NAMES, "bounds": BOUNDS}


def unpack(row):
    p = {}
    for i, n in enumerate(NAMES):
        lo, hi, sc = PROBLEM_DEF[n]
        v = row[i]
        p[n] = 10 ** v if sc == "log" else v
    return p


def rhs(t, y, p):
    M, IMACCD, ACCD, E, S = y
    EtO_nM = p["EtO"] * 1e3
    f_ind = EtO_nM ** 1.22 / (1960.0 ** 1.22 + EtO_nM ** 1.22)
    g_plp = p["PLP"] / (p["Kd_PLP"] + p["PLP"])
    Scap = p["S_Max"] * 1e6
    cap = 1.0 - S / Scap

    v_txn = p["k_transcript"] * (p["leak_per"] + (1 - p["leak_per"]) * f_ind)
    v_mat = p["k_fold"] * IMACCD * g_plp
    v_tat = p["k_tatcat"] * p["TatAyCy"] * ACCD / (p["K_tat"] + ACCD)
    k_unbind = p["k_off"] / N_LYSM_FIXED
    v_on = p["k_on"] * E * cap
    v_off = k_unbind * S

    dM = v_txn - p["dm"] * M
    dIMACCD = p["k_transrate"] * M - v_mat - p["k_deg_u"] * IMACCD
    dACCD = v_mat - v_tat
    dE = v_tat + v_off - v_on - p["d_spread"] * E
    dS = v_on - v_off
    return [dM, dIMACCD, dACCD, dE, dS]


def model_outputs(p):
    y0 = [IC] * 5
    t_eval_grid = np.concatenate(([0], np.logspace(-2, np.log10(T_EVAL), 300)))
    t_eval_grid = np.minimum(t_eval_grid, T_EVAL)
    t_eval_grid[-1] = T_EVAL
    try:
        sol = solve_ivp(rhs, (0, T_EVAL), y0, method="BDF", args=(p,),
                         rtol=1e-6, atol=1e-12, t_eval=t_eval_grid, max_step=T_EVAL / 50)
        if not sol.success:
            raise RuntimeError(sol.message)
        S = np.clip(sol.y[4], 0, None)
    except Exception:
        sol = solve_ivp(rhs, (0, T_EVAL), y0, method="LSODA", args=(p,),
                         rtol=1e-6, atol=1e-12, t_eval=t_eval_grid)
        S = np.clip(sol.y[4], 0, None)
    Sf = S[-1]
    if Sf <= 0:
        return 0.0, np.nan
    idx = np.argmax(S >= Sf / 2)
    t_half = t_eval_grid[idx] if S[idx] >= Sf / 2 else np.nan
    return Sf, t_half


# ============================================================
# Morris サンプリング & 評価
# ============================================================
if __name__ == "__main__":
    R = 20  # 軌道数
    X = morris_sample.sample(problem, N=R, num_levels=4, seed=1)
    print(f"評価回数: {X.shape[0]} (r={R}, k={len(NAMES)})")

    Y_S = np.zeros(X.shape[0])
    Y_T = np.zeros(X.shape[0])
    for i, row in enumerate(X):
        p = unpack(row)
        Sf, th = model_outputs(p)
        Y_S[i] = Sf
        Y_T[i] = th
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{X.shape[0]}")

    # log変換して解析（出力が桁で動くため。感度解析は log10(S), log10(t_half) に対して行う）
    Y_S_log = np.log10(np.clip(Y_S, 1e-12, None))
    valid_T = np.isfinite(Y_T) & (Y_T > 0)
    Y_T_log = np.where(valid_T, np.log10(np.where(Y_T > 0, Y_T, np.nan)), np.nan)

    res_S = morris_analyze.analyze(problem, X, Y_S_log, num_levels=4, seed=1, print_to_console=False)
    # t_half に NaN があると SALib が扱えないため、有効な行だけで再解析はできない(軌道が壊れる)ので
    # NaNを大きな値(T_EVALの10倍のlog)で埋めて「立ち上がらない」を表現
    Y_T_filled = np.where(np.isfinite(Y_T_log), Y_T_log, np.log10(T_EVAL * 10))
    res_T = morris_analyze.analyze(problem, X, Y_T_filled, num_levels=4, seed=1, print_to_console=False)

    def to_table(res):
        rows = []
        for i, n in enumerate(res["names"]):
            rows.append({
                "name": n,
                "mu": float(res["mu"][i]),
                "mu_star": float(res["mu_star"][i]),
                "sigma": float(res["sigma"][i]),
                "mu_star_conf": float(res["mu_star_conf"][i]),
            })
        rows.sort(key=lambda r: -r["mu_star"])
        return rows

    table_S = to_table(res_S)
    table_T = to_table(res_T)

    out = {"n_eval": int(X.shape[0]), "r": R, "T_eval_s": T_EVAL,
           "S_quantity_log10": table_S, "t_half_speed_log10": table_T,
           "n_lysm_fixed": N_LYSM_FIXED}
    with open("morris_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("\n=== 量: log10(S at 72h) ===")
    print(f"{'param':<14}{'mu':>10}{'mu*':>10}{'sigma':>10}{'mu*/|mu|':>10}")
    for r in table_S:
        ratio = r["mu_star"] / abs(r["mu"]) if abs(r["mu"]) > 1e-12 else float("inf")
        print(f"{r['name']:<14}{r['mu']:>10.3f}{r['mu_star']:>10.3f}{r['sigma']:>10.3f}{ratio:>10.2f}")

    print("\n=== 速さ: log10(t_half) ===")
    print(f"{'param':<14}{'mu':>10}{'mu*':>10}{'sigma':>10}{'mu*/|mu|':>10}")
    for r in table_T:
        ratio = r["mu_star"] / abs(r["mu"]) if abs(r["mu"]) > 1e-12 else float("inf")
        print(f"{r['name']:<14}{r['mu']:>10.3f}{r['mu_star']:>10.3f}{r['sigma']:>10.3f}{ratio:>10.2f}")

    print("\nsaved: morris_results.json")

    # %%
  import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("morris_results.json", "r", encoding="utf-8") as f:
    d = json.load(f)

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
rows = d["S_quantity_log10"]
names = [r["name"] for r in rows]
mu_star = [r["mu_star"] for r in rows]
sigma = [r["sigma"] for r in rows]

ax.scatter(mu_star, sigma, s=40, color="#2C5F2D")
for n, x, y in zip(names, mu_star, sigma):
    ax.annotate(n, (x, y), fontsize=9, xytext=(4, 4), textcoords="offset points")
mmax = max(max(mu_star), max(sigma)) * 1.1
ax.plot([0, mmax], [0, mmax], "--", color="#AAAAAA", linewidth=1, label="sigma = mu*")
ax.set_xlabel("mu* (log10 S at 72h)")
ax.set_ylabel("sigma (log10 S at 72h)")
ax.set_title("Morris screening: quantity output S(72h)")
ax.legend()
plt.tight_layout()
plt.savefig("morris_S_quantity.png", dpi=150)
print("saved: morris_S_quantity.png")
# %%
