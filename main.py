import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
from collections import defaultdict
from models import split_by_whitespace, RatingModel, get_sentence
from models import parse_paragraph_2, parse_paragraph_3
import torch
# from vocab import get_glove, build_char_dict

GLOVE_DIM = 100
NOT_EXIST = torch.FloatTensor(1, GLOVE_DIM).zero_()


def visualize_dataset(input1):
    input_df1 = pd.read_csv(input1, sep='\t')
    dict_worker_scores = input_df1[['workerid', 'Rating']].groupby('workerid')['Rating'].apply(list).to_dict()
    # input_df2 = pd.read_csv(input2, sep='\t', lineterminator='\r')= []
    mean_value = []
    for (k, v) in dict_worker_scores.items():
        values = np.array(v)
        mean_value.append(np.mean(values))
    plt.hist(mean_value, 6, density=True, facecolor='g', alpha=0.75)
    plt.hist(mean_value, 6)
    plt.show()
    print(len(dict_worker_scores))
    dict_sentence_scores = input_df1[['Item', 'Rating']].groupby('Item')['Rating'].apply(list).to_dict()
    mean_value = []
    for (k, v) in dict_sentence_scores.items():
        values = np.array(v)
        mean_value.append(np.mean(values))
    plt.hist(mean_value, 6)
    plt.show()
    print(len(dict_sentence_scores))


def load_dataset(input1, input2):
    input_df1 = pd.read_csv(input1, sep='\t')
    input_df2 = pd.read_csv(input2, sep='\t')
    dict_item_paragraph = input_df2[['Item_ID', '20-b']].groupby('Item_ID')['20-b'].apply(list).to_dict()
    dict_sentence_scores = input_df1[['Item', 'Rating']].groupby('Item')['Rating'].apply(list).to_dict()
    dict_item_mean_score = dict()
    for (k, v) in dict_sentence_scores.items():
        values = np.array(v)
        dict_item_mean_score[k] = np.mean(values)
    dict_item_sentence = input_df1[['Item', 'Sentence']].drop_duplicates().groupby('Item')['Sentence'].apply(list).to_dict()
    return (dict_item_mean_score, dict_item_sentence, dict_item_paragraph)


def find_bucket(input_file):
    unique_bucket_lst = []
    idx_value = defaultdict(list)
    input_df = pd.read_csv(input_file)
    temp_set = set()
    acc_value = 0
    num_b = 0
    for index, row in input_df.iterrows():
        temp_set.add(row['Item'])
        acc_value += row['Rating']
        if not (index+1) % 10:
            num_b += 1
            flag = 0
            idx = len(unique_bucket_lst)
            # for u in unique_bucket_lst:
            for i in range(len(unique_bucket_lst)):
                u = unique_bucket_lst[i]
                dif = temp_set.difference(u)
                if len(dif) == 0:
                    flag = 1
                    idx = i
                    break
                elif len(dif) < 10:
                    print("diff:", index, temp_set, i, u, dif)
                    return

            if flag == 0:
                unique_bucket_lst.append(temp_set)

            # if temp_set not in unique_bucket_lst:
            #     unique_bucket_lst.append(temp_set)

            # else:
            #     print(num_b, unique_bucket_lst.index(temp_set))
            # idx = unique_bucket_lst.index(temp_set)
            idx_value[idx].append(acc_value/10.0)
            temp_set = set()
            acc_value = 0
        # print(len(unique_bucket_lst))
    # print(num_b)
    # print(len(idx_value))
    v_mean = []
    for k, v in idx_value.items():
        if (len(v) > 1):
            print(k, unique_bucket_lst[k])
            v_np = np.array(v)
            v_mean.append(np.mean(v_np))
            # print(k, v_np, np.mean(v_np), np.std(v_np))
            # print(np.std(v_np))
        else:
            v_mean.append(1.0*v[0])
    print(np.mean(np.array(v_mean)), np.std(np.array(v_mean)))
    # plt.hist(v_mean, 10)
    # plt.show()
    # print(len(v_mean))
    # if (len(v) > 1):
    #     print(k, len(v))
    # print("---")
    # print(index,row['Item'], row['workerid'])


def load_sentences_only(input):
    input_df = pd.read_csv(input, sep='\t')
    sentence_list = input_df['Sentence'].tolist()
    sentence_set = set(sentence_list)
    some_pos = []
    for s in sentence_set:
        s = re.sub('[^a-zA-Z0-9 \n\.]', '', s)
        tokens = split_by_whitespace(s)
        some_pos.append(tokens.index('some'))
    plt.hist(some_pos, 100)
    plt.show()


def main():
    # load_sentences_only("./some_database.csv")
    # visualize_dataset("./some_database.csv")
    labels, contents, contexts = load_dataset("./some_database.csv", "./swbdext.csv")
    # emb_matrix, word2id, id2word = get_glove(FLAGS.glove_path, FLAGS.embedding_size)
    # find_bucket("Book1.csv")
    # print(len(labels), len(contents))
    # sentence_len = []
    # for (k,v) in contents.items():
    #     temp = split_by_whitespace(v[0])
    #     sentence_len.append(len(temp))
    # plt.hist(sentence_len, 20)
    # plt.show()

    curr_max = 0
    curr_min = 100
    original_labels = []
    for (k, v) in labels.items():
        if v > curr_max:
            curr_max = v
        if v < curr_min:
            curr_min = v
    # normalize the values
    normalized_labels = []
    max_diff = curr_max - curr_min
    keys = []
    for (k, v) in labels.items():
        keys.append(k)
        original_labels.append(float(v))
        labels[k] = (float(v) - curr_min) / max_diff
        normalized_labels.append(labels[k])
    print(keys)
    content_embs = []
    plain_embs = []
    content_embs = []
    for (k, v) in contents.items():  # <-- only the target
        curr_emb, _ = get_sentence(v[0])
        content_embs.append(curr_emb)

    # for (k, v) in contents.items():  # <-- Two Sentences
    #     curr_emb, target_tokens = get_sentence(v[0])
    #     next_emb, next_emb_2 = parse_paragraph_2(contexts[k][0], target_tokens)
    #     if torch.eq(next_emb, NOT_EXIST).all() and torch.eq(next_emb_2, NOT_EXIST).all():
    #         content_embs.append(curr_emb)
    #     # elif torch.eq(next_emb, NOT_EXIST).all():
    #     #     content_embs.append(curr_emb*np.float64(0.6)+next_emb_2*np.float64(0.4))
    #     elif torch.eq(next_emb_2, NOT_EXIST).all():
    #         content_embs.append(curr_emb*np.float64(0.6)+next_emb*np.float64(0.4))
    #     else:
    #         content_embs.append(curr_emb*np.float64(0.6)+next_emb*np.float64(0.2)+next_emb_2*np.float64(0.2))
    #     # print(curr_emb, content_embs[len(content_embs)-1])
    #     plain_embs.append(curr_emb)

    # for (k, v) in contents.items():  # <-- Three Sentences
    #     keys.append(k)
    #     curr_emb, target_tokens = get_sentence(v[0])
    #     next_emb, next_emb_2, next_emb_3 = parse_paragraph_3(contexts[k][0], target_tokens)
    #     if torch.eq(next_emb, NOT_EXIST).all() and torch.eq(next_emb_2, NOT_EXIST).all() and torch.eq(next_emb_3, NOT_EXIST).all():
    #         content_embs.append(curr_emb)
    #     elif torch.eq(next_emb_2, NOT_EXIST).all() and torch.eq(next_emb_3, NOT_EXIST).all():
    #         # content_embs.append(curr_emb*np.float64(1.0/2)+next_emb*np.float64(1.0/2))
    #         content_embs.append(curr_emb*np.float64(0.6)+next_emb*np.float64(0.4))
    #     elif torch.eq(next_emb_3, NOT_EXIST).all():
    #         # content_embs.append(curr_emb*np.float64(1.0/2)+next_emb*np.float64(1.0/2/2)+next_emb_2*np.float64(1.0/2/2))
    #         content_embs.append(curr_emb*np.float64(0.6)+next_emb*np.float64(0.2)+next_emb_2*np.float64(0.2))
    #     else:
    #         # content_embs.append(curr_emb*np.float64(1.0/2)+next_emb*np.float64(1.0/2/2)+next_emb_2*np.float64(1.0/2/2/2)+next_emb_3*np.float(1.0/2/2/2))
    #         content_embs.append(curr_emb*np.float64(0.6)+next_emb*np.float64(0.2)+next_emb_2*np.float64(0.2/2)+next_emb_3*np.float(0.2/2))
    #     # print(curr_emb, content_embs[len(content_embs)-1])
    #     plain_embs.append(curr_emb)

    # r_model = RatingModel("./")
    # r_model.train(torch.stack(content_embs), np.array(normalized_labels))

    # evaluate
    # r_model_content = RatingModel("./", "./Model_3S/RNet_epoch_100.pth", is_train=False)
    # preds_content = r_model_content.evaluate(torch.stack(content_embs), max_diff, curr_min)

    r_model_decay = RatingModel("./", "./Model_0S/RNet_epoch_500.pth", is_train=False)
    preds_decay = r_model_decay.evaluate(torch.stack(content_embs), max_diff, curr_min)

    # i = 0
    # for i in range(len(keys)):
    #     if preds_content[i] < 4 and preds_content[i] > 2 and original_labels[i] > 1 and original_labels[i] < 5:
    #         print(keys[i], preds_content[i], original_labels[i])

    # print(len(original_labels), preds.shape, len(content_embs))
    # print(np.corrcoef(preds_decay, np.array(original_labels)))
    x_axis = np.arange(len(original_labels))
    # print(curr_max, curr_min)
    print(len(keys), len(original_labels))

    f = open('./predictions.csv', 'w')
    head_line = "Item_ID\toriginal_mean\tpredicted\n"
    f.write(head_line)
    for i in range(len(keys)):
        k = keys[i]
        ori = original_labels[i]
        pre = preds_decay[i]
        curr_line = k + '\t' + format(ori) + '\t' + format(pre)
        f.write(curr_line+"\n")
    f.close()
    # plt.subplot(2, 1, 1)
    # plt.scatter(preds_content, np.array(original_labels), s=5, c='r', label="100 epochs")
    # plt.scatter(preds_decay, np.array(original_labels), s=5, c='b', label="500 epochs")
    # plt.xlim(1, 7)
    # plt.ylim(1, 7)
    # plt.xlabel('predictions')
    # plt.ylabel('real ratings')
    # function = [i for i in range(1, 1001, 7)]
    # plt.plot(function, function, c='k', label="real rating = preds")
    # plt.legend()
    # plt.title("Target sentence only, implicature strength rating")
    # plt.show()
    return

if __name__ == "__main__":
    main()