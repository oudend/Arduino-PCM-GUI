from scipy.fftpack import fft
import numpy as np
from scipy.io import wavfile # get the api
import PySimpleGUI as sg 
import soundfile # pip install soundfile
import librosa
import math
import os

#! pip install pipreqs


def rescale_linear(array, new_min, new_max):
    """Rescale an arrary linearly."""
    minimum, maximum = np.min(array), np.max(array)
    m = (new_max - new_min) / (maximum - minimum)
    b = new_min - m * minimum
    return m * array + b

layout = [[sg.Text("Choose audio file: "), sg.Input(), sg.FileBrowse(key="-Audio-", file_types=(("wav Files", "*.wav"),("mp3 Files", "*.mp3"),), tooltip='Which audio file to convert')], [sg.Text("Choose a output directory: "), sg.Input(), sg.FolderBrowse(key="-Folder-", tooltip='Which folder to save output to')], [sg.Text("Sample rate: "), sg.Input("8000", key='-SAMPLE_RATE-', tooltip='The sample rate to convert to(8000 recommended)'), sg.Checkbox("change sample rate", key='-CHANGE_SAMPLE_RATE-', default=True, tooltip='Off means the original sample rate is preferred(True recommended)')], [sg.Combo(["8bit", "4bit", "2bit"], "8bit", key="-BITS-", readonly=True), sg.Checkbox("convert bits", key='-CONVERT_BITS-', default=True, tooltip='Will convert audio to 8bit(should only be off if it is already 8bit)'), sg.Text("Bit range", tooltip="The trimming range for 2bit and 4bit audio"), sg.Input("127", key="-TRIM_RANGE-")], [sg.Checkbox("rescale", key='-RESCALE-', default=False, tooltip='Will make low sample rates louder(8bit only)')], [sg.Button('Calculate'), sg.Button('Quit')], [sg.Text(size=(60,1), key='-ERROR-', text_color='red')]]

window = sg.Window('PCMO', layout)

while True:
        event, values = window.Read()
        
        if event in ('Quit', None):
            break 
        if event == 'Calculate':
            print(values)
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

print(values)

#-RESCALE-

#TODO: write immediately to .txt


# Your new sampling rate
# new_rate = 49.89 # 48000

# Read file
#original_sampling_rate, raw_data = wavfile.read(f'./underground.wav') # load the data

#new_sampling_rate = 7000

data, data_sample_rate = librosa.load(sound_file)#f'./letyoudown.wav')

data = librosa.to_mono(data) #average all channels into one channel

if change_sample_rate:
    data = librosa.resample(data, orig_sr=data_sample_rate, target_sr=sample_rate)

# number_of_samples = round(len(raw_data) * float(new_sampling_rate) / original_sampling_rate)
# downsampled_data = sps.resample(raw_data, number_of_samples)


# soundfile.write('8bit.wav', downsampled_data, new_sampling_rate, subtype='PCM_U8')

# soundfile.write('8bitUnsampled.wav', raw_data, original_sampling_rate, subtype='PCM_U8')

# channel0 = []

# downsample_channel0 = downsampled_data[:, 0]

# for sample in downsample_channel0:
#     channel0.append(min( 254, math.floor(sample/(2**8))))

if convert_bits:
    soundfile.write(f'{save_folder}/8bit.wav', data, sample_rate, subtype='PCM_U8') # write the data
    _, data = wavfile.read(f'{save_folder}/8bit.wav') # load the data

#data[data > 254] = 254 #? redundant now without compression

# try:
#     channel0 = data[:, 0]
# except IndexError:
#     channel0 = data

packed_data = []

current_sample = None



if bits == "4bit":
    mult = 4
    bitNum = 4
elif bits == "2bit":
    mult = 6
    bitNum = 2

#bit_range = 100 # default = 127
print("bit range: ", bit_range)
bit_half = (255 - bit_range) // 2

if bits == "2bit" or bits == "4bit":
    print(f"converting to {bits} format")
    bit_max = 8 / bitNum
    for index, sample in enumerate(data):

        eightbit_sample = math.floor(sample / 2) * 2 #! eightbit_sample is for trimming the range

        if eightbit_sample < bit_half:
            eightbit_sample = bit_half
        elif eightbit_sample > bit_range + bit_half: # 127 + 64
            eightbit_sample = bit_range + bit_half

        twobit_sample = ( eightbit_sample - bit_half ) // 2**(mult-1)

        #twobit_sample = math.floor(sample / (2**mult)) #? this should also be changed depending on bits

        if index % bit_max == 0: #? change 4 to bit_max
            current_sample = twobit_sample
        else:
            #print((index % bit_max))
            current_sample = current_sample | twobit_sample << (bitNum * int(index % bit_max)) #? change 2 * to bits *
            #eightbit_data[math.floor(index / 4)] = twobit_sample
            if  index % bit_max == bit_max - 1: #? change 3 to bit_max - 1
                packed_data.append(current_sample)
    data = packed_data

if rescale:
    if bits == "8bit":
        data = rescale_linear(data, 0, 255).astype(int) #! works best for low sample rates
    # else:# if bits == "2bit":
    #     data = rescale_linear(data, 0, 3).astype(int)
    #     print("rescaling 2bit")

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


# for string in dataStringList:

#     if string == lastString:
#         count += 1

#         compressedStringArray[length] = f"255,{string},{count}" #used to be x

#         if count > 254:
#             low_byte = count & 0x00FF
#             high_byte = count >> 8

#             compressedStringArray[length] = f"255,{string},255,{low_byte},{high_byte}"

#         lastString = string
#         continue
#     else:
#         if count == 1:
#             debugLength += 1
#         else:
#             debugLength += 3

#     count = 1
#     compressedStringArray.append(f"{string}") #used to be just string
#     length += 1

#     lastString = string


# compressedChannel0String = ",".join(compressedStringArray)



print('file length: ', len(dataList))

with open(f'{save_folder}/{tail}.h', 'w') as f:
     f.write("const unsigned char defaultSample [] PROGMEM = {\n%s,\n};" % (dataString) )

# with open(f'{save_folder}/compressed.h', 'w') as f:
#      f.write("const unsigned char compressedSample [] PROGMEM = {\n%s,\n};" % (compressedChannel0String) )



##todo, try decompressing it in python first and then implement it in pcmReader.h


# with open('compressed.h', 'w') as f:
#     f.write("""const char compressedAudio[] PROGMEM = {"%s"};""" % (compressedChannel0String))

# with open('bells.h', 'w') as f:
#     f.write("const unsigned char sample [] PROGMEM = {\n%s,\n};" % (compressedChannel0String) )