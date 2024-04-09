##############################################################################################################
#    @author Somiljain7
#    @author Ritesh Kumar
##############################################################################################################
import argparse
import textgrid  # pip install textgrid
import os


def convert_to_srt_time(seconds):
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    srt_time = "%d:%02d:%02d,%03d" % (hours, minutes, seconds, milliseconds)
    return srt_time


def txtgrid_read(f_name, tier_name='sentence-IPA-transcription'):
    tg = textgrid.TextGrid.fromFile(f_name)
    sbt = {}
    for i, interval_tier in enumerate(tg):
        # print(i)
        if interval_tier.name == tier_name:
            for j, current_tier in enumerate(interval_tier):
                # print(j, current_tier.mark)
                sbt[j] = [convert_to_srt_time(current_tier.minTime), convert_to_srt_time(
                    current_tier.maxTime), current_tier.mark]
    return sbt


def convert_to_srt(dict_obj, srt_file_path):
    srt_file = open(srt_file_path, 'w')
    start_time = [dict_obj[i][0] for i in dict_obj]
    end_time = [dict_obj[i][1] for i in dict_obj]
    txt = [dict_obj[i][2] for i in dict_obj]
    for i in range(len(dict_obj)):
        srt_file.write(str(i + 1) + '\n')
        srt_file.write(
            f'{start_time[i].replace(".", ",")} --> {end_time[i].replace(".", ",")}\n')
        srt_file.write(f'{txt[i]}\n\n')


def srt_final(f_name, tier_name='sentence-IPA-transcription'):
    a = txtgrid_read(f_name, tier_name)
    srt_file_path = f_name.split(".")[0]+".srt"
    convert_to_srt(a, srt_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-audio', type=str,
                        help="Input audio file/directory")
    args = parser.parse_args()

    wav_file = args.in_audio

    tier_name = 'sentence-IPA-transcription'

    if os.path.isdir(wav_file):
        for root_dir, all_dirs, all_files in os.walk(wav_file):
            for current_file in all_files:
                file_path = os.path.join(root_dir, current_file)
                print('Processing', file_path)
                if file_path.endswith('.TextGrid'):
                    srt_final(file_path, tier_name)
    else:
        srt_final(wav_file)
