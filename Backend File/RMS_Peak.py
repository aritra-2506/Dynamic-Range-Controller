import math
from flask import Flask, json, send_file, request, jsonify, render_template
from flask_cors import CORS
from scipy.io import wavfile
from werkzeug.utils import secure_filename
from scipy.io.wavfile import read
import numpy as np
from scipy.io.wavfile import write
import csv
import wave


app = Flask(__name__)
CORS(app)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

#----------------------------------------RMS-----------------------------------------------------------------------

@app.route("/getSuccessOriginalFile", methods = ['GET', 'POST'])
def getTheSuccessOriginalFile():
    if request.method == 'POST':

        ff = request.files['file']

        ff.save(secure_filename('OriginalFile.wav'))
    return jsonify({"sucess": "true"})


@app.route("/getOriginalFile")
def getTheOriginalFile():
    return send_file('OriginalFile.wav')


@app.route("/getFile")
def getTheFile():
    return send_file('compressed.wav')


@app.route("/results", methods = ['POST'])
def results():
    if request.method == 'POST':
        ratio = request.form['Ratio']
        threshold = request.values['Threshold']
        attack = request.form['Attack']
        release = request.form['Release']


        fieldnames = ['ratio', 'threshold','attack','release']
        with open('param.csv', 'w') as inFile:
            writer = csv.DictWriter(inFile, fieldnames=fieldnames)
            writer.writerow({'ratio': ratio, 'threshold': threshold,'attack':attack,'release': release})


        return '{} {} {} {}'.format(ratio, threshold, attack, release)


@app.route("/recFile", methods = ['GET', 'POST'])
def  recFile():

    if request.method == 'GET':

        #ff = request.files['file']

        #ff.save(secure_filename(ff.filename))
        with open("param.csv") as f:
            reader = csv.reader(f)
            data = [r for r in reader]
            ratio = float(data[0][0])
            threshold = float(data[0][1])
            attack = float(data[0][2])
            release = float(data[0][3])

            samplerate, data = wavfile.read("OriginalFile.wav")
            print(samplerate)
            w = wave.open('OriginalFile.wav', 'rb')
            num = w.getnchannels()

            # CT = -40
            CT = threshold
            # ct= 32768*(np.power(10, CT/20))
            # ct1=10 * (np.log10(ct))
            # CR = 20
            CR = ratio
            # at = 0.0001  # in second
            at = attack
            # rt = 0.004  # in second
            rt = release
            g = 1
            Fs = samplerate
            rms = 0
            tav = 0.01
            output = np.array([], dtype=float)
            norm_data = np.array([], dtype=float)

            song = read("OriginalFile.wav")
            data = np.array(song[1], dtype=float)

            if (num == 1):
                for t in data:  # converting stereo to mono channel
                    avg_data = t / 32768
                    norm_data = np.append(norm_data, avg_data)
            else:
                for t in data:  # converting stereo to mono channel
                    avg_data = t[0] / 32768
                    norm_data = np.append(norm_data, avg_data)

            a = -2.2 / (at * Fs)
            b = -2.2 / (rt * Fs)

            at = 1 - math.exp(a)
            rt = 1 - math.exp(b)
            # print(at,rt)

            CS = 1 - (1 / CR)
            # print(CS)

            for i, item in enumerate(norm_data):
                rms = ((1 - tav) * rms + tav * (np.power(item, 2)))
                X = 10 * (np.log10(rms))
                ab = (CS * (CT - X))
                G = min(0, ab)
                newG = G / 20
                f = np.power(10, newG)
                if (f < g):
                    coefficient = at
                else:
                    coefficient = rt
                g = (1 - coefficient) * g + coefficient * f
                # print(g)
                if (i == 0):
                    val = 0
                else:
                    val = (norm_data[i - 1] * g)
                output = np.append(output, val)

            # scaled = np.int16(output / np.max(np.abs(output)) * 32767)  # 16-bit PCM range from-32768 to +32767 for int16
            scaled = np.int16(output * 32767)
            write('compressed.wav', Fs, scaled)

        return jsonify({"sucess": "true"})

#----------------------------Peak---------------------------------------------------------------------------

@app.route("/getSuccessOriginalFile1", methods = ['GET', 'POST'])
def getTheSuccessOOriginalFile1():
    if request.method == 'POST':

        ff = request.files['file']

        ff.save(secure_filename('OriginalFile1.wav'))
    return jsonify({"sucess": "true"})

@app.route("/getOriginalFile1")
def getTheOriginalFile1():
    return send_file('OriginalFile1.wav')

@app.route("/getFile1")
def getTheFile1():
    return send_file('compressed_peak.wav')

@app.route("/results1", methods = ['POST'])
def results1():
    if request.method == 'POST':
        ratio = request.form['Ratio']
        threshold = request.values['Threshold']
        attack = request.form['Attack']
        release = request.form['Release']


        fieldnames = ['ratio', 'threshold','attack','release']
        with open('param1.csv', 'w') as inFile:
            writer = csv.DictWriter(inFile, fieldnames=fieldnames)
            writer.writerow({'ratio': ratio, 'threshold': threshold,'attack':attack,'release': release})


        return '{} {} {} {}'.format(ratio, threshold, attack, release)


@app.route("/recFile1", methods = ['GET', 'POST'])
def  recFile1():

    if request.method == 'GET':

        #ff = request.files['file']

        #ff.save(secure_filename(ff.filename))
        with open("param1.csv") as f:
            reader = csv.reader(f)
            data = [r for r in reader]
            ratio = float(data[0][0])
            threshold = float(data[0][1])
            attack = float(data[0][2])
            release = float(data[0][3])

        samplerate, data = wavfile.read("OriginalFile1.wav")
        print(samplerate)
        w = wave.open('OriginalFile1.wav', 'rb')
        num = w.getnchannels()

        #CT = -40
        CT = threshold
        #CR = 20
        CR = ratio
        #at = 0.0001  # in second
        at = attack
        #rt = 0.004  # in second
        rt = release
        g = 1
        duty = 10  # Duty of the signal in seconds
        f = 500.0  # Frequency of the signal
        Fs = samplerate
        X = 0
        i = 0
        k = 0
        total = 0
        output = np.array([], dtype=float)
        norm_data = np.array([], dtype=float)
        # xpeak = np.array([],dytype=float)
        xpeak = 0;
        x_sc_op = 0;

        song = read("OriginalFile1.wav")
        data = np.array(song[1], dtype=float)  # song[0] = sample_rate , song[1] = data

        if (num == 1):
            for t in data:  # converting stereo to mono channel
                avg_data = t / 32768
                norm_data = np.append(norm_data, avg_data)
        else:
            for t in data:  # converting stereo to mono channel
                avg_data = t[0] / 32768
                norm_data = np.append(norm_data, avg_data)

        a = -2.2 / (at * Fs)
        b = -2.2 / (rt * Fs)

        at = 1 - math.exp(a)
        rt = 1 - math.exp(b)
        # print(at,rt)

        CS = 1 - (1 / CR)
        # print(CS)

        for i, item in enumerate(norm_data):
            if np.any(i == 0 or xpeak < item):
                coefficient = at
            else:
                coefficient = rt
            # print(coefficient)

            xpeak = (1 - coefficient) * xpeak + coefficient * abs(item);

            # print(xpeak)

            xpeak_log = 20 * (np.log10(xpeak));
            # print(xpeak_log)

            # GainReduction - -----------------------------------
            m = CS * (CT - xpeak_log);
            GR = min([0, m]);
            # print(GR)

            # Sidechainfactor - ---------------------------------
            ab = GR / 20;
            x_sc = np.power(10, ab);
            # print(x_sc)

            # SmoothingFilter - ---------------------------------
            if np.array(i == 0 or x_sc_op > x_sc):
                coefficient = at;
            else:
                coefficient = rt;

            # print(coefficient)

            x_sc_op = (1 - coefficient) * x_sc_op + coefficient * x_sc;
            # print(x_sc_op)

            val = x_sc_op * norm_data[i];
            # print(val)

            output = np.append(output, val)

        scaled = np.int16(output * 32767)
        write('compressed_peak.wav', Fs, scaled)

        return jsonify({"sucess": "true"})
    #----------------------------------------Limiter-----------------------------------------------------------------------


@app.route("/getSuccessOriginalFile2", methods = ['GET', 'POST'])
def getTheSuccessOOriginalFile2():
    if request.method == 'POST':

        ff = request.files['file']

        ff.save(secure_filename('OriginalFile2.wav'))
    return jsonify({"sucess": "true"})

@app.route("/getOriginalFile2")
def getTheOriginalFile2():
    return send_file('OriginalFile2.wav')

@app.route("/getFile2")
def getTheFile2():
    return send_file('compressed_lim.wav')

#gc.collect()

@app.route("/results2", methods = ['POST'])
def results2():
    if request.method == 'POST':
        #ratio = request.form['Ratio']
        threshold = request.values['Threshold']
        attack = request.form['Attack']
        release = request.form['Release']


        fieldnames = ['threshold','attack','release']
        with open('param2.csv', 'w') as inFile:
            writer = csv.DictWriter(inFile, fieldnames=fieldnames)
            writer.writerow({'threshold': threshold,'attack':attack,'release': release})


        return '{} {} {}'.format(threshold, attack, release)


@app.route("/recFile2", methods = ['GET', 'POST'])
def  recFile2():

    if request.method == 'GET':

        #ff = request.files['file']

        #ff.save(secure_filename(ff.filename))
        with open("param2.csv") as f:
            reader = csv.reader(f)
            data = [r for r in reader]
            threshold = float(data[0][0])
            attack = float(data[0][1])
            release = float(data[0][2])

        samplerate, data = wavfile.read("OriginalFile2.wav")
        print(samplerate)
        w = wave.open('OriginalFile2.wav', 'rb')
        num = w.getnchannels()

        CT1 = threshold
        newG = CT1 / 20
        CT = np.power(10, newG)
        # CT = 0.5
        # print(CT)
        # CR = 1
        at = attack  # in second
        rt = release  # in second
        Fs = samplerate
        xpeak = 0
        g = 1;
        output = np.array([], dtype=float)
        # output = np.append(output, 0)
        norm_data = np.array([], dtype=float)

        print(Fs)

        song = read("OriginalFile2.wav")
        data = np.array(song[1], dtype=float)

        if (num == 1):
            for t in data:  # converting stereo to mono channel
                avg_data = t / 32768
                norm_data = np.append(norm_data, avg_data)
        else:
            for t in data:  # converting stereo to mono channel
                avg_data = t[0] / 32768
                norm_data = np.append(norm_data, avg_data)

        for i, item in enumerate(norm_data):
            a = np.abs(item)
            # print(xd)

            if (a > xpeak):
                coeff = at
            else:
                coeff = rt
            # print(a)
            xpeak = ((xpeak * (1 - coeff)) + (coeff * a))
            # print(xd)
            f = min(1, CT / xpeak)
            if (f < g):
                coeff = at
            else:
                coeff = rt
            g = ((1 - coeff) * g + (coeff * f))
            if (i == 0):
                val = 0
            else:
                val = (norm_data[i - 1] * g)
            output = np.append(output, val)


        scaled = np.int16(output * 32767)
        write('compressed_lim.wav', Fs, scaled)

        return jsonify({"sucess": "true"})
    
#------------------------------------------NoiseGate--------------------------------------------------------------------------

@app.route("/getSuccessOriginalFile3", methods = ['GET', 'POST'])
def getTheSuccessOriginalFile3():
    if request.method == 'POST':

        ff = request.files['file']

        ff.save(secure_filename('OriginalFile3.wav'))
    return jsonify({"sucess": "true"})

@app.route("/getOriginalFile3")
def getTheOriginalFile3():
    return send_file('OriginalFile3.wav')

@app.route("/getFile3")
def getTheFile3():
    return send_file('compressed_NSGT.wav')
 
#gc.collect()

@app.route("/results3", methods = ['POST'])
def results3():
    if request.method == 'POST':
        ltr = request.values['LTRThreshold']
        upr = request.values['UPRThreshold']
        attack = request.form['Attack']
        release = request.form['Release']
        hld = request.form['HldTm']
        pp = request.form['ppt']


        fieldnames = ['ltr', 'upr','attack','release','hld','pp']
        with open('param3.csv', 'w') as inFile:
            writer = csv.DictWriter(inFile, fieldnames=fieldnames)
            writer.writerow({'ltr': ltr, 'upr': upr,'attack':attack,'release': release,'hld':hld,'pp':pp})


        return '{} {} {} {} {} {}'.format(ltr, upr, attack, release,hld,pp)


@app.route("/recFile3", methods = ['GET', 'POST'])
def  recFile3():

    if request.method == 'GET':

        #ff = request.files['file']

        #ff.save(secure_filename(ff.filename))
        with open("param3.csv") as f:
            reader = csv.reader(f)
            data = [r for r in reader]
            ltr = float(data[0][0])
            upr = float(data[0][1])
            attack = float(data[0][2])
            release = float(data[0][3])
            hld = float(data[0][4])
            pp = float(data[0][5])

            samplerate, data = wavfile.read("OriginalFile3.wav")
            #print(samplerate)
            w = wave.open('OriginalFile3.wav', 'rb')
            num = w.getnchannels()

            lt1 = ltr
            lt = np.power(10, (lt1 / 20))
            at1 = attack
            rt1 = release
            a = pp
            ht1 = hld
            ut1 = upr
            ut = np.power(10, (ut1 / 20))
            Fs = samplerate

            output1 = np.array([], dtype=float)
            output = np.array([], dtype=float)
            norm_data = np.array([], dtype=float)
            g = np.array([], dtype=float)
            h = np.array([], dtype=float)
            x1 = np.array([], dtype=float)

            song = read("OriginalFile3.wav")
            data = np.array(song[1], dtype=float)

            if (num == 1):
                for t in data:  # converting stereo to mono channel
                    avg_data = t / 32768
                    norm_data = np.append(norm_data, avg_data)
            else:
                for t in data:  # converting stereo to mono channel
                    avg_data = t[0] / 32768
                    norm_data = np.append(norm_data, avg_data)

            rel = round(rt1 * Fs)
            att = round(at1 * Fs)
            lthcnt = 0
            uthcnt = 0
            ht = round(ht1 * Fs)

            s = np.absolute(norm_data[0])
            x1 = np.append(x1, s)
            c = (np.power((1 - a), 2) * s)
            h = np.append(h, c)

            s = np.absolute(norm_data[1]) + 2 * a * x1[0]
            x1 = np.append(x1, s)
            c = (np.power((1 - a), 2) * s)
            h = np.append(h, c)

            for i, item in enumerate(norm_data):
                if (i >= 2):
                    s = (np.absolute(norm_data[i]) + (2 * a * x1[i - 1]) - (np.power(a, 2)) * x1[i - 2])
                    x1 = np.append(x1, s)
                    c = np.power((1 - a), 2) * s
                    h = np.append(h, c)

            h = h / max(h)

            for i, item in enumerate(h):
                if (i == 0):
                    lthcnt = lthcnt + 1
                    uthcnt = uthcnt + 1
                    q = 0
                    g = np.append(g, q)
                    # output1 = np.append(output1, g)
                else:
                    if (h[i] <= lt) | ((h[i] < ut) & (lthcnt > 0)):
                        lthcnt = lthcnt + 1
                        uthcnt = 0
                        if (lthcnt > ht):
                            if (lthcnt > (rel + ht)):
                                q = 0
                                g = np.append(g, q)
                            else:
                                q = 1 - (lthcnt - ht) / rel
                                g = np.append(g, q)
                        elif ((i < ht) & (lthcnt == i)):
                            q = 0
                            g = np.append(g, q)
                        else:
                            q = 1
                            g = np.append(g, q)
                    elif (h[i] >= ut) | ((h[i] > lt) & (uthcnt > 0)):
                        uthcnt = uthcnt + 1

                        if (g[i - 1] < 1):
                            q = max(uthcnt / att, g[i - 1])
                            g = np.append(g, q)
                        else:
                            q = 1
                            g = np.append(g, q)
                        lthcnt = 0
                    else:
                        q = g[i - 1]
                        g = np.append(g, q)
                        lthcnt = 0
                        uthcnt = 0

                y = norm_data[i] * g[i]
                output1 = np.append(output1, y)
            val = output1 * max(np.absolute(norm_data)) / max(np.absolute(output1))
            output = np.append(output, val)

            scaled = np.int16(output * 32767)
            write('compressed_NSGT.wav', Fs, scaled)

        return jsonify({"sucess": "true"})


if __name__ == "__main__":
    app.run(threaded=True)



