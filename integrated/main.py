# -*- coding: utf-8 -*-

import random
import time
import argparse
import torch
import torch.nn as nn
from torch.autograd import Variable
from torch import optim
from comet_ml import Experiment
from data_loader import *
from training import *
"""
Created on Wed Nov  8 22:31:02 2017

@author: eduardofierro
"""

######## File params ########

parser = argparse.ArgumentParser()
parser.add_argument('--MIN_LENGTH', type=int, default=5, help='Min Length of sequence')
parser.add_argument('--MAX_LENGTH', type=int, default=200, help='Max Length of sequence')
parser.add_argument('--MIN_LENGTH_TARGET', type=int, default=5, help='Min Length of sequence (Output side)')
parser.add_argument('--MAX_LENGTH_TARGET', type=int, default=200, help='Max Length of sequence (Output side)')
parser.add_argument('--lang1', type=str, default="en", help='Input Language')
parser.add_argument('--lang2', type=str, default="fr", help='Target Language')
parser.add_argument('--teacher_forcing_ratio', type=float, default=0.5, help='Teacher forcing ratio for encoder')
parser.add_argument('--hidden_size', type=int, default=256, help='Size of hidden layer')
parser.add_argument('--n_iters', type=int, default=3000, help='Number of single iterations through the data')
parser.add_argument('--learning_rate', type=float, default=0.01, help='Learning rate (for both, encoder and decoder)')
parser.add_argument('--n_layers', type=int, default=1, help='Number of layers (for both, encoder and decoder)')
parser.add_argument('--dropout_enc', type=float, default=0.1, help='Dropout (%) in the encoder')
parser.add_argument('--dropout_dec', type=float, default=0.1, help='Dropout (%) in the decoder')
parser.add_argument('--model_type', type=str, default="seq2seq", help='Model type (and ending of files)')
parser.add_argument('--main_data_dir', type=str,
                    default="/Users/eduardofierro/Google Drive/TercerSemetre/NLP/ProjectOwn/Data/Model_ready/",
                    help='Directory where data is saved (containing folders tain/dev/test)')
parser.add_argument('--out_dir', type=str, default=".", help="Directory to save the models state dict")
parser.add_argument('--save_every', type=int, default=5000, help='Checkpoint model after number of iters')
parser.add_argument('--print_every', type=int, default=5000, help='Print training loss after number of iters')
# translation params
parser.add_argument('--enc_checkpoint', type=str, default=".", help="checkpoint to load encoder from (Default: None)")
parser.add_argument('--dec_checkpoint', type=str, default=".", help="checkpoint to load decoder from (Default: None)")
parser.add_argument('--outlang_checkpoint', type=str, default=".", help="checkpoint to load outlang from")

opt = parser.parse_args()
print(opt)

######## Comet ML ########

# experiment = Experiment(api_key="00Z9vIf4wOLZ0yrqzdwHqttv4", log_code=True)
# hyper_params = vars(opt)
# experiment.log_multiple_params(hyper_params)

#################################
# Languages classes and imports #
#################################

# flag for character encoding
target_char = (opt.model_type == 'bpe2char')


#########
# Train #
#########
def main():
    use_cuda = torch.cuda.is_available()
    input_lang, output_lang, pairs = prepare_data(opt.lang1, opt.lang2, do_filter=True, min_length_input=opt.MIN_LENGTH,
                                                  max_length_input=opt.MAX_LENGTH, min_length_target=opt.MIN_LENGTH_TARGET,
                                                  max_length_target=opt.MAX_LENGTH_TARGET, normalize=False, reverse=False,
                                                  path=opt.main_data_dir, char_output=target_char)
    torch.save(output_lang, "{}/output_lang.pth".format(opt.out_dir))
    encoder1 = EncoderRNN(input_lang.n_words, opt.hidden_size, opt.n_layers, dropout_p=opt.dropout_enc)
    attn_decoder1 = AttnDecoderRNN(opt.hidden_size, output_lang.n_words,
                                   opt.n_layers, dropout_p=opt.dropout_dec)

    if use_cuda:
        encoder1 = encoder1.cuda()
        attn_decoder1 = attn_decoder1.cuda()

    trainIters(input_lang, output_lang, encoder1, attn_decoder1, n_iters=opt.n_iters, pairs=pairs, pairs_eval=pairs_dev, learning_rate=opt.learning_rate, print_every=5000, char=target_char, opt=opt)

    torch.save(encoder1.state_dict(), "{}/saved_encoder_final.pth".format(opt.out_dir))
    torch.save(attn_decoder1.state_dict(), "{}/saved_decoder_final.pth".format(opt.out_dir))


if __name__ == '__main__':
    main()