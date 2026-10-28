import numpy as np
import wfdb
from scipy import signal

FS = 250                       # target sample rate (MIT-BIH is 360 Hz)
WIN = 32                       # integrator window, same as Verilog
BEATS = set("NLRBAaJSVrFejnE/fQ")

def pan_tompkins(x, fs=FS, win=WIN):
    sos = signal.butter(2, [5, 15], 'bandpass', fs=fs, output='sos')
    bp = signal.sosfilt(sos, x)                                   # causal bandpass
    d = np.convolve(bp, [1, 2, 0, -2, -1])[:len(x)]               # derivative
    sq = d ** 2                                                   # squaring
    mwi = np.convolve(sq, np.ones(win) / win)[:len(x)]            # moving integrator

    # adaptive threshold, processed sample by sample like hardware
    refractory = int(0.2 * fs)
    spki = 0.5 * np.max(mwi[:2 * fs])
    npki = 0.1 * spki
    thr = npki + 0.25 * (spki - npki)
    last = -refractory
    dets = []
    for n in range(2, len(mwi)):
        is_peak = mwi[n-1] > mwi[n-2] and mwi[n-1] >= mwi[n]
        if not is_peak:
            continue
        p, v = n - 1, mwi[n - 1]
        if p - last <= refractory:
            continue
        if v > thr:
            spki = 0.125 * v + 0.875 * spki
            last = p
            lo = max(0, p - int(0.3 * fs))
            dets.append(lo + int(np.argmax(np.abs(bp[lo:p + 1]))))  # locate R peak
        else:
            npki = 0.125 * v + 0.875 * npki
        thr = npki + 0.25 * (spki - npki)
    return np.array(dets), bp, mwi

def score(det, ann, tol):
    det = np.sort(det)
    used = np.zeros(len(det), bool)
    tp = 0
    for a in ann:
        i = np.searchsorted(det, a)
        best = None
        for j in (i - 1, i):
            if 0 <= j < len(det) and not used[j] and abs(det[j] - a) <= tol:
                if best is None or abs(det[j] - a) < abs(det[best] - a):
                    best = j
        if best is not None:
            used[best] = True
            tp += 1
    return tp, len(det) - tp, len(ann) - tp   # TP, FP, FN

def load(rec):
    sig, _ = wfdb.rdsamp(rec, pn_dir='mitdb', channels=[0])
    x = signal.resample_poly(sig[:, 0], 25, 36)               # 360 Hz -> 250 Hz
    ann = wfdb.rdann(rec, 'atr', pn_dir='mitdb')
    a = np.array([round(s * FS / 360) for s, c in zip(ann.sample, ann.symbol) if c in BEATS])
    return x, a[a >= 2 * FS]

if __name__ == "__main__":
    records = ['100', '101', '103', '105', '106', '108', '109', '111']
    TP = FP = FN = 0
    print("record   beats    Se(%)   PPV(%)")
    for r in records:
        x, a = load(r)
        det, _, _ = pan_tompkins(x)
        det = det[det >= 2 * FS]
        tp, fp, fn = score(det, a, tol=int(0.15 * FS))
        TP += tp; FP += fp; FN += fn
        print(f"{r:>6} {len(a):7d}  {100*tp/(tp+fn):7.2f}  {100*tp/(tp+fp):7.2f}")
    print(f" TOTAL {TP+FN:7d}  {100*TP/(TP+FN):7.2f}  {100*TP/(TP+FP):7.2f}")

    # export 20 s of record 100 as 16-bit hex for the Verilog testbench
    x, a = load('100')
    ints = np.round(x[:20 * FS] * 200).astype(np.int16)       # 200 ADC units per mV
    with open('data/ecg100.hex', 'w') as f:
        for v in ints:
            f.write(f"{int(v) & 0xFFFF:04x}\n")
    print("wrote data/ecg100.hex with", len(ints), "samples")
