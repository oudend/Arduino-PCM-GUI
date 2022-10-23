from scipy.fftpack import fft
import numpy as np
from scipy.io import wavfile # get the api
import PySimpleGUI as sg 
import soundfile # pip install soundfile
import librosa
import math
import os

def rescale_linear(array, new_min, new_max):
    """Rescale an arrary linearly."""
    minimum, maximum = np.min(array), np.max(array)
    m = (new_max - new_min) / (maximum - minimum)
    b = new_min - m * minimum
    return m * array + b

layout = [[sg.Text("Choose audio file: "), sg.Input(), sg.FileBrowse(key="-Audio-", file_types=(("wav Files", "*.wav"),("mp3 Files", "*.mp3"),), tooltip='Which audio file to convert')], [sg.Text("Choose a output directory: "), sg.Input(), sg.FolderBrowse(key="-Folder-", tooltip='Which folder to save output to')], [sg.Text("Sample rate: "), sg.Input("8000", key='-SAMPLE_RATE-', tooltip='The sample rate to convert to(8000 recommended)'), sg.Checkbox("change sample rate", key='-CHANGE_SAMPLE_RATE-', default=True, tooltip='Off means the original sample rate is preferred(True recommended)')], [sg.Combo(["8bit", "4bit", "2bit", "1bit"], "8bit", key="-BITS-", readonly=True), sg.Checkbox("convert bits", key='-CONVERT_BITS-', default=True, tooltip='Will convert audio to 8bit(should only be off if it is already 8bit)'), sg.Text("Bit range", tooltip="The trimming range for 2bit and 4bit audio"), sg.Input("127", key="-TRIM_RANGE-")], [sg.Checkbox("rescale", key='-RESCALE-', default=False, tooltip='Will make low sample rates louder(8bit only)')], [sg.Button('Calculate'), sg.Button('Quit')], [sg.Text(size=(60,1), key='-ERROR-', text_color='red')]]

window = sg.Window('PCMO', layout)

while True:
        event, values = window.Read()
        
        if event in ('Quit', None):
            break 
        if event == 'Calculate':
            if values["-Audio-"] and values["-Folder-"]:
                break
            window['-ERROR-'].update("You need to provide both output folder and audio file!")
window.close()

sound_file = values["-Audio-"]
save_folder = values["-Folder-"]

sample_rate = int(values["-SAMPLE_RATE-"])
bit_range = int(values["-TRIM_RANGE-"])
convert_bits = values["-CONVERT_BITS-"] #! rename
bits = values["-BITS-"]
rescale = values["-RESCALE-"]
change_sample_rate = values["-CHANGE_SAMPLE_RATE-"]

head, tail = os.path.split(sound_file)

tail = tail.split(".")[0]

if bits == "4bit":
    bit_mult = 4
    bitNum = 4
elif bits == "2bit":
    bit_mult = 6
    bitNum = 2
elif bits == "1bit":
    bit_mult = 7
    bitNum = 1

#print(values)

#-RESCALE-

#TODO: write immediately to .txt


data, data_sample_rate = soundfile.read(sound_file)#librosa.load(sound_file)#f'./letyoudown.wav')

data = data.T

data = librosa.to_mono(data) #average all channels into one channel

if change_sample_rate:
    data = librosa.resample(data, orig_sr=data_sample_rate, target_sr=sample_rate)

if convert_bits:
    soundfile.write(f'{save_folder}/8bit.wav', data, sample_rate, subtype='PCM_U8') # write the data
    _, data = wavfile.read(f'{save_folder}/8bit.wav') # load the data

packed_data = []

current_sample = None


#bit_range = 100 # default = 127
print("bit range: ", bit_range)

if bits != "8bit":
    print(f"converting to {bits} format")

    bit_half = (255 - bit_range) // 2
    bit_max = 8 / bitNum

    for index, sample in enumerate(data):

        eightbit_sample = math.floor(sample / 2) * 2 #! eightbit_sample is for trimming the range

        if eightbit_sample < bit_half:
            eightbit_sample = bit_half
        elif eightbit_sample > bit_range + bit_half: # 127 + 64
            eightbit_sample = bit_range + bit_half

        twobit_sample = ( eightbit_sample - bit_half ) // 2**(bit_mult-1)

        if index % bit_max == 0:
            current_sample = twobit_sample
        else:
            #print((index % bit_max))
            current_sample = current_sample | twobit_sample << (bitNum * int(index % bit_max))
            #eightbit_data[math.floor(index / 4)] = twobit_sample
            if  index % bit_max == bit_max - 1:
                packed_data.append(current_sample)
    data = packed_data

if rescale:
    if bits == "8bit":
        data = rescale_linear(data, 0, 255).astype(int) #! works best for low sample rates

if bits == "8bit": #! UGLY AS FUCK
    dataList = data.tolist()
else:
    dataList = data

dataStringList = [str(int) for int in dataList]

dataString = ','.join(dataStringList)

### COMPRESSION ###

compressedStringArray = []

count = 1
incrementing = False
lastString = None

length = -1

debugLength = 0

print('file length: ', len(dataList))

with open(f'{save_folder}/{tail}.h', 'w') as f:
     f.write("const unsigned char defaultSample [] PROGMEM = {\n%s,\n};" % (dataString) )