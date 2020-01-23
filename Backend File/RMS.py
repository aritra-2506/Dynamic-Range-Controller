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


if __name__ == "__main__":
    app.run(threaded=True)




