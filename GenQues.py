import json
import requests
from underthesea import sent_tokenize, pos_tag

URL = 'http://localhost:8000/ner'

NER2QUES_MAPPING = {
    'PERSON': ['người', 'Là ai ?'],
    'LOCATION': ['cái gì', ''],
    'ORGANIZATION': ['cái gì', ''],
    'DATETIME': ['vào thời gian nào', '']
}

# Lấy danh sách NER:


def get_ner_from_text(text):
    PARAMS = {
        "sentences": [
            {
                "text": text
            }
        ]
    }
    r = requests.post(url=URL, json=PARAMS)
    return r.json()

# Kiểm tra độ dài của câu.


def check_len_text(text):
    return len(text.split())

# Dựa vào POS để lấy một phần của câu để ghép thành câu hỏi.


def check_pos(tag, postag_list):
    if tag == "PERSON":
        # lặp từng POS nếu câu mới bắt đàu bởi trạng từ hoặc trợ động từ thì láy câu đó để trả về
        for i in range(0, len(postag_list)):
            # Nếu nó là dấu thì bỏ qua tính đến TH tiếp theo
            if postag_list[i][1] == 'CH':
                continue
            # Nếu theo sau là trợ động từ và động từ
            elif (postag_list[i][1] == 'R' and postag_list[i+1][1] == "V") or (postag_list[i][1] == "V"):
                return i
            return -1

    if tag == "DATETIME":
        for i in range(0, len(postag_list)):
            # Nếu nó là dấu thì bỏ qua tính đến TH tiếp theo
            if postag_list[i][1] == 'CH' and postag_list[i+1][1] != 'CH':
                return i
            return -1


# Kiểm tra Text có thể convert sang ques tương ứng.
def check_text2ques(entity, text):
    tag = entity['tag']
    if tag == 'PERSON':
        if check_len_text(text) < 7:
            return False
        # danh sách kết quả đánh POS của câu.
        pos_tagging = pos_tag(text)
        i = check_pos(tag, pos_tagging)
        if i == -1:
            return False
        return True

    if tag == "DATETIME":
        # kiểm tra
        pos_tagging = pos_tag(text)
        i = check_pos(tag, pos_tagging)
        pos_tagging = pos_tag(text)
        if i == -1:
            return False
        return True

# Tiến hành xử lý câu đầu vào phụ thuộc vào loại thực thể .


def process_text_with_entity(entity, text):
    new_text = text
    entity_tag = entity['tag']
    entity_text = entity['text']

    # if entity_tag == 'PERSON':
    #     new_text = text[entity['end_position']:].strip()
    # elif entity_tag == 'DATETIME':
    #     new_text = text[:entity['start_position']]+text[entity['end_position']:]
    return new_text


# Trả về loại câu hỏi ứng với loại thực thể
def gen_question_from_entity(entity, new_text):
    _text = entity['text']
    _tag = entity['tag']
    _start = entity['start_position']
    _end = entity['end_position']

    pre_text = new_text[:_start]
    end_text = new_text[_end:]

    if _tag == "PERSON":
        question = new_text[:_start]+NER2QUES_MAPPING[_tag][0] + \
            new_text[_end:]+' '+NER2QUES_MAPPING[_tag][1]
    else:
        question = new_text[:_start]+NER2QUES_MAPPING[_tag][0] + \
            new_text[_end:]
        if question[-1] == '.':
            question = question[:-1]
        question += ' ?'
    return question

    # if _tag == 'PERSON':
    #     _pos_tag = pos_tag(new_text)
    #     i = check_pos(_tag,_pos_tag)
    #     ques = "Ai "+" ".join([pos[0] for pos in _pos_tag[i:]])
    #     if ques[-1] == '.':
    #         ques = ques[:-2]
    #     ques+= ' ?'
    #     print(ques)
    #     return ques
    # if _tag == 'DATETIME':
    #     _pos_tag = pos_tag(new_text)
    #     i = check_pos(_tag,_pos_tag)
    #     ques = "Vào thơì gian nào "+" ".join([pos[0] for pos in _pos_tag[i:]])
    #     if ques[-1] == '.' or ques[-1] == ',':
    #         ques = ques[:-2]
    #     ques+= ' ?'
    #     print(ques)
    #     return ques

# Tiến hành lấy câu hỏi từ text


def get_question_from_text(text):
    result = []
    # Tách các thực thể
    result = get_ner_from_text(text)
    entities = result['result'][0]['entities']
    new_text = result['result'][0]['text']
    print("raw text: ", text)
    for entity in entities:
        new_text = process_text_with_entity(entity, new_text)
        # if check_text2ques(entity,new_text):
        print("Ques: ", gen_question_from_entity(entity, new_text))


def pipe_line(paragraph):
    # Tiến hành tách Para thành các text.
    texts = sent_tokenize(paragraph)
    print(texts)
    for text in texts:
        get_question_from_text(text)
        print('='*20)


if __name__ == "__main__":

    # paragraph = "Cách mạng Tháng Mười Nga năm 1917 thành công, các dân tộc không phải Nga trong đế quốc Nga được  giải phóng, lần lượt tách ra thành các quốc gia dân tộc độc lập. Sau nội chiến (1918 – 1920), xuất phát từ nhu cầu hợp tác kinh tế và phòng  thủ  chống  ngoại  xâm,  Liên  bang  Cộng  hòa  xã  hội  chủ  nghĩa  Xô  -  viết (Liên Xô) được thành lập ngày 30-12-1922 gồm 4 nước CHXV là Nga, Ucraina, Bêlarút và Ngoại Cápcadơ3. Sau đó các nước CHXV gia nhập Liên Xô tăng dần, đến năm 1940 là 15 nước.  Tình đoàn kết giữa các nước CHXV đã giúp Liên Xô chiến  thắng  chủ  nghĩa  phát  xít  trong  chiến  tranh  vệ  quốc  (1941  –  1945)  và đạt được  những  thành  tựu  to  lớn  trong  công  cuộc  xây  dựng  chủ  nghĩa  xã  hội,  trở thành  cường  quốc  thứ  hai  thế  giới  sau  Mĩ.  Mặc  dầu  vậy,  trong  công  cuộc  xây dựng  chủ  nghĩa  xã  hội,  Liên  Xô đã  phạm phải  không ít  sai  lầm,  thiếu  sót.  Thất bại  của  công  cuộc  cải  tổ đã  làm  cho  Liên  Xô  tan  rã. Ngày  8-12-1991,  các  tổng thống  Nga,  Ucraina,  Bêlarút đã  ra  tuyên  bố  chung  :  Liên  Xô  không  còn  tồn  tại nữa và kí Hiệp ước thành lập Cộng đồng các quốc gia độc lập (SNG). Ng ày 21- 12-1991,  tại  thủ đô  Anma  Ata  ( Cadắcxtan),  8  nước  Adécbaidan,  Ácmênia, Cadắcxtan, Kiếcghidia, Mônđavia, Tuốcmênia,  Tátgikistan, Udơbêkistan gia nhập Hiệp ước nói trên sau khi đã kí (với từng nước Nga, Ucraina, Bêlarút) vào bản  tuyên  bố  về  mục đích  và  nguyên  tắc  của  SNG  .  Tháng  10-1993,  Grudia đã trở thành thành viên chính thức của tổ chức này, nâng số thành viên SNG lên 12 nước.  Tháng  8-2005,  Tuốcmênia  rút  khỏi  quy  chế  thành  viên  chính  thức,  chỉ tham  gia  với  tư cách  là  quan  sát  viên.  Do  vậy,  cơ  cấu  của  SNG  là  11  +  1.  Cho đến  nay,  SNG đã  gặt  hái được  những  thành  công  nhất định,  nhưng  cũng  không hoàn  toàn  được  như  mong  muốn.  Các  nước  Mônđavia,  Ucraina  và  Tuốcmênia"
    # get_question_from_text(text)
    text1 = 'Chủ tịch Quốc hội Vương Đình Nhuệ sẽ tới thăm trường THPT Bắc Cạn A, một ngôi trường thật đẹp.'
    text2 = "(Dân trí) - Tổng thống Volodymyr Zelensky tuyên bố Ukraine sẽ giành lại Crimea, sau khi bán đảo này sáp nhập vào Nga năm 2014."
    text3 = "Tổng thống Zelensky nói trong bài phát biểu hôm 4/9."
    text4 = "Tổng thống Ukraine mới đây tuyên bố, việc khôi phục hòa đàm với Nga chỉ có thể thực hiện nếu quân đội Nga rút khỏi \"các vùng lãnh thổ chiếm đóng\" của Ukraine."
    text5 = "ngày 19-01-2018 , Tổng thống Nga Putin đã khánh thành cây cầu dài 19km trị giá 4 tỷ USD nối Crimea với đất liền Nga."
    text6 = 'chiều ngày 2-9 vừa qua, Lâm Đồng đón 85.000 lượt khách, trong đó du khách chủ yếu tới thăm quan, nghỉ dưỡng tại TP Đà Lạt.'
    text7 = "Liên quan đến tình trạng ngập úng cục bộ ngày 1-9 vừa qua tại TP Đà Lạt, lãnh đạo UBND TP Đà Lạt vừa có cuộc họp trực tuyến với các phòng ban, đơn vị, UBND các xã, phường."
    parapraph = text1+' '+text2+' '+text3+' '+text4+' '+text5
    parapraph1 = "Ngô Sĩ Liên đã dựa vào hai bộ sử của Lê Văn Hưu và Phan Phu Tiên để làm công việc đó. Ông cho rằng hai bộ sách của họ Lê và họ Phan tuy \"rõ ràng, có thể xem được\" (蹟彰可鑒 - chương chương khả giám) nhưng \"ghi chép còn có chỗ chưa đủ, nghĩa lệ còn có chỗ chưa đáng, văn tự còn có chỗ chưa ổn, người đọc không khỏi có chỗ còn chưa vừa ý\" (而記志猶有未僃義例猶有未當文字猶有未安讀者不能無憾焉 - nhi ký chí do hữu vị bị, nghĩa lệ do hữu vị thường, văn tự do hữu vị an, độc giả bất năng vô hám yên)[8]. Do vậy, ông đã sửa chữa chép lại hai bộ sách này \"có việc nào sót quên thì bổ sung thêm vào, có lệ nào chưa đúng thì cải chính lại, văn có chỗ nào chưa ổn thì đổi đi, gián hoặc có việc hay dở có thể khuyên răn được thì góp thêm ý kiến quê mùa ở sau\" (事有遺忘者補之例有未當者正之文有未安者改之間有善惡可以勸懲者贅鄙見於其後 - Sự hữu di vong giả bổ chi, lệ hữu vị đáng giả chính chi, văn hữu vị an giả cải chi, gian hữu thiện ác khả dĩ khuyên trừng giả, chuế bỉ kiến ư kì hậu). Ngô Sĩ Liên cũng giữ lại cho bộ sử nhiều lời bình của Lê Văn Hưu và Phan Phu Tiên về các sự kiện lịch sử. Không chỉ sửa chữa sử cũ, Ngô Sĩ Liên còn bổ sung vào dòng chảy lịch sử Việt Nam thời đại họ Hồng Bàng, đưa nó trở thành thời đại đầu tiên trong lịch sử thay vì nhà Triệu như trong Đại Việt sử ký của Lê Văn Hưu. Trong quá trình biên soạn, bên cạnh các bộ chính sử trước đó và sử sách Trung Quốc,[11] Ngô Sĩ Liên cũng đã thu thập tư liệu từ nhiều nguồn khác, bao gồm dã sử, các bản truyện chí có thể là Việt điện u linh tập hay Lĩnh Nam chích quái cùng với những lời truyền tụng. Tuy là truyền thuyết và truyện dân gian nhưng chúng vẫn được Ngô Sĩ Liên xem là nguồn sử liệu đáng tin cậy.[12] Đây là lần đầu tiên các nguồn kiểu này được một nhà sử học Việt Nam sử dụng trong tác phẩm lịch sử."
    pipe_line(paragraph=parapraph1)
