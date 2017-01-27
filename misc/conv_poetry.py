#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

POETRIES = [
    (1, "大吉", "七寶浮圖塔\\n高峰頂上安\\n眾人皆仰望\\n莫作等閒看", "就像出現了用美麗寶石做成的佛塔般地，似乎會有非常好的事情。因為能改用放眼萬事的立場，可以得到周圍的人們的信賴吧。合乎正道的你的行為，能被很多人的認同及鼓勵。不用隨便的態度看事情，用正確的心思會招來更多的好的結果。願望：會充分地實現吧。疾病：會治癒吧。盼望的人：會出現吧。遺失物：變得遲遲地才 ： 找到吧。蓋新居、搬家、嫁娶、旅行、交往等：全部很好吧。萬事行為謹慎。粗心大意行事的話，就會發生意想之外的災害吧。"),
    (2, "小吉", "月被浮雲翳\\n立事自昏迷\\n幸乞隂公祐\\n何慮不開眉", "似乎抱著強烈的願望，但是照目前的樣子，似乎無法達成願望。因為光是想著要怎麼作，持續著沒有決心的情形。為了人而變得盡全力努力，幸福將會來到。似乎會有令人高興的事情發生。根據這件好事，不擔心未來的事也沒有關係了。願望：因為持續不斷地努力 ： ，必定會實現。疾病：雖然拖長，但是之後可以康復吧。盼望的人：遲遲地才出現吧。遺失物：不能找出來吧。交往：要節制吧。蓋新居、搬家：都不壞吧。結親緣、旅行：順利進行吧。"),
    (3, "兇", "愁惱損忠良\\n青宵一炷香\\n雖然防小過\\n閑慮覺時長", "層層疊疊嘆氣與苦惱，被回報的事很少吧。就像向著天燒香祈禱般地，你的願望無法傳達天聽吧。雖這樣說，但就算只有一點點善行也好，作了可以逃離災厄吧。東想西想之間，似乎不知不覺就像過了很長的時間。等待時機的到來吧。願望：難實現吧。疾病：雖然拖長，但是會治好吧。遺失物：難以找到吧。盼望的人：要花很久的時間吧。旅行：因為很壞，放棄吧。蓋新居搬家：勉勉強強地算好吧。結婚交往：要節制吧。"),
    (4, "吉", "累有興雲志\\n君恩祿未封\\n若逢侯手印\\n好事始總總", "拼命地要出人頭地，可以看出你的志向。但是遺憾地是，你的不成熟還不能得到居上位者的認同。然而，就像是如果已經寫了好文章的話，就立刻得到認同般地，好好傳遞自己的心思是很重要的。好事也似乎會越來越接踵而起吧。願望：能實現吧。如果這樣的話，終生幸福吧。疾病：變得遲遲地才會治好 ： 吧。遺失物：遲遲地才找到吧。盼望的人：會出現吧。旅行：途中要忍耐各式各樣的困難吧。蓋新居、搬家、結親緣、交往：萬事都好吧。"),
    (5, "兇", "家道未能昌\\n危々保禍殃\\n暗雲侵月桂\\n佳人一炷香", "就算試著努力家業，和努力相比卻難以繁盛起來吧。不是一生災禍，只是危險的事比較多而已吧。像烏雲遮月一樣，一生阻礙比較多吧。在身份高貴的婦人房裡，各種想法像香一樣擴散開來般，心裡無法平靜吧。願望：難以實現吧。疾病：難治好吧。遺失物：難找到吧。盼望的人：不會出現吧。蓋新居、搬家：先放棄，暫時觀察情況再說吧。結親緣、旅行、交往：因為萬事兇惡，請諸行為慎重行事。"),
    (6, "末吉", "宅墓鬼凶多\\n人事有爻訛\\n傷財防損失\\n祈福始中和", "家中恐怕有災禍。行為慎重，抱著深深的信心，這樣可以帶來好的結果。個人的問題或遭遇，過錯或過失很多，事情難以進展吧。就算破財，也會有所得。因為竭盡祈求神佛的力量，自己盡力努力，能到幸福吧。願望：難以實現吧。疾病：康復很花時間吧。遺失物：難找到吧。盼望的人：遲遲地才出現吧。蓋新居、搬家：好吧。旅行：好吧。結親緣、交往：壞吧。"),
    (7, "兇", "登舟待便風\\n月色暗朦朧\\n欲輾香輪去\\n高山千万重", "像風不吹船無法前進一樣，就算採取行動也難以向前發展吧。就像月亮被烏雲籠罩著，前後都無法看見一樣，對事情，似乎作一些莽撞的行為。為了逃離災難，想請託別人教導怎麼作，但是況狀似乎變得很困難。就像在登險峻的重重山巒車子難行般地，就算思考各種手段，事情的解決還是困難吧。但是現在還是靜靜的過生活吧。願望：難以實現吧。疾病：難以治癒吧。遺失物：難以找到吧。盼望的人：不會出現吧。蓋新居、搬家：換時間吧。結親緣、喜慶祝賀、旅行、交往：不好吧。"),
    (8, "大吉", "勿頭中見尾\\n文華須得理\\n禾刀自偶然\\n当遇非常喜", "在腦海裡沒有對失敗或結果的恐懼，抬頭挺胸地朝著目標達成而努力吧。無論是文學或武術都能得到真理，要有充實自己的心態吧。就像用刀來割稻般地，會得到成果，幸福會自然地到來吧。如果正心地守道的話，可以變得幸福吧。願望：會實現吧。疾病：會治好。請注意養生吧。遺失物：可以找到吧。盼望的人：會出現吧。蓋新居、搬家、交往：是好事吧。旅行：途中請不要粗心大意吧。結親緣：全都是好的吧。"),
    (9, "大吉", "有名須得遇\\n三望一朝遷\\n貴人来指処", "按照所想的，夢想實現，名聲也廣傳人間吧。就像三個願望可以完全的實現般地，全部能一次完全的被實現吧。從比自己身份地位高的人，給予各式各樣令人欣喜的事吧。像是隨著四季循環花會開、會結果一樣，每天努力會有成果，好運會展開吧。願望：會實現吧。疾病：會治好吧。遺失物：會找到吧。盼望的人：會出現吧。蓋新居、搬家：好吧。結親緣、交往：全都好吧。旅行：沒問題吧。"),
    (10, "大吉", "舊用多成破\\n新更始見財\\n改求雲外望\\n枯木遭春開", "過去的不幸或許多煩惱也會消去，好事將發生吧。隨著新的願望的出現，財富也會增加。就像是在雲上追求願望般地，請試著追求高高的願望。像枯木在春天開花一樣，一定會變得很繁盛吧。願望：會實現吧。疾病：會治好吧。遺失物：立刻會找到吧,盼望的人：會出現吧。蓋新居、搬家：會變為好結果吧。結親緣、旅行、交往：全部變為好結果吧。"),
    (11, "大吉", "有禄興家業\\n文華達帝都\\n雲中乗好箭\\n兼得貴人扶", "幸福與收入具足，家業也漸漸繁盛起來吧。才能顯現出來，可得世人的好評價吧。就算是向空中放箭也可以得到好的獵物般地，任何事也都可以成功吧。得到這樣的幸福之外，加上還可以得到居上位者或神佛的幫助吧。願望：會充分地實現吧。疾病：會治好吧。遺失物：會找到吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：沒問題吧。結婚、交往：全部都能得到好結果吧。"),
    (12, "大吉", "楊柳遇春時\\n残花発旧枝\\n重々霜雪裡\\n黄金色更輝", "像柳樹也逢春增添綠色般地，希望也會出現吧。像老枝也發芽，開花般地，喜事會到來吧。像在重重霜或雪中般地，無論怎樣過去的勞苦不斷吧，但是像黃金色無論到何時，都閃亮耀眼般地，不要忘以前的勞苦，用誠實的心過生活吧。願望：會實現吧。疾病：會變好吧。遺失物：會回來吧。盼望的人：晚出現吧。蓋新居、搬家：會成為好結果吧。旅行：沒有阻礙吧。結婚、交往：全都適當吧。"),
    (13, "大吉", "手把大陽輝\\n東君發舊枝\\n稼苗方欲秀\\n猶更上雲梯", "如果時機來到的話，抱著勇氣努力做事，可以過著充實的生活吧。就像是老枝條，隨著春天到來，花就開了一樣，運勢會開展吧。就像稻苗也是如果春天來了的話，就會生長般地，你也會繁榮昌盛吧。像是也能爬上難登的雲梯般，因為更加地持續努力就會成功吧。願望：會實現吧。疾病：會治好吧。遺失物：立刻找就能找到吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：在春天和夏天好吧。結婚、交往：全部都好吧。"),
    (14, "末吉", "玉石未分時\\n憂心轉更悲\\n前途通大道\\n花發應殘枝", "就像是就算有寶玉，哪一個是寶石哪一個是石頭還分不清楚般地，沒辦法分辨事物的狀況。就算是想要出人頭地，但會為了各式各樣的事情而心痛、嘆息、悲傷也說不定。如果忍耐勞苦，將來自然地看得到未來的去向吧。然後像枯枝開花般地，願望會實現吧。願望：很花時間但會實現吧。疾病：會拖長吧，但是不會影響性命吧。遺失物：難出現吧。盼望的人：似乎會變得遲吧。蓋新居、搬家：不太好吧。結婚：現在要節制，如果往後的話好吧。旅行、交往：避開吧。"),
    (15, "凶", "年乖數亦孤\\n久病未能蘇\\n岸危舟未發\\n龍臥失明珠", "朋友年年地減少，變成孤單一人，生活變得不自由吧。長期的疾病雖然種種地想治癒，但是卻康復無望吧。就像船想靠岸，因為危險不能靠岸般地，想做點什麼，但是因為有阻礙，總是不能著手進行吧。像是龍失去重要的龍珠般地，人也失去希望吧。願望：難以實現吧。疾病：危險吧。遺失物：難找回吧。盼望的人：不會出現吧。蓋新居、搬家：都不好吧。旅行、結親緣：壞吧。"),
    (16, "吉", "破改重成望\\n前途喜亦寧\\n貴人相助處\\n祿馬照前程", "拋開至今為止的願望，期待別的願望為佳吧。要前往的目的地有令人欣喜的事，變為安穩的心情吧。因為得到居上位者（觀世音菩薩）的幫助，越來越得到力量吧。像是用馬載著上天給予的寶物，前方光明照耀般地，在人世間地位或收入等也和想的一樣地充滿吧。願望：能被實現吧。疾病：會康復吧。遺失物：會出現吧。盼望的人：會來吧。蓋新居、搬家：會有好結果吧。旅行：好吧。結親緣、交往：全部會變成好結果吧。"),
    (17, "凶", "怪異防憂惱\\n人宅見分離\\n惜華還值雨\\n杯酒惹閑非", "如果作一些想要防止降落在自己身上的危險的事的話，反而煩惱似乎變多了。不知不覺間，不好的事情持續著，似乎會有家人分離的事。就像捨不得花凋謝的話，更是會被雨淋凋萎般地，不好的是似乎持續著。因為無法按照所想的發展，沈溺於喝酒之類的，似乎還是會產生壞想法吧。願望：難實現吧。疾病：康復需要長時間吧。遺失物：不會出現吧。盼望的人：不會出現吧。蓋新居、搬家：先放棄，暫時觀察情況再說吧。旅行：似乎引起壞的結果吧。婚事、交往：全部不好吧。"),
    (18, "吉", "離暗出明時\\n麻衣變綠衣\\n舊憂終是退\\n遇祿應交輝", "就像烏雲的天空也漸漸地晴朗，可以看到月亮般地，今後漸漸地希望能被實現吧。就像脫掉破舊的衣服，穿著漂亮的衣服般地，用全新的心情做好每天的善行吧。長時間的悲傷也漸漸地消散吧。福德自然地增加，人生光輝閃耀吧。願望：會實踐吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結親緣、交往：全部變為好結果吧。"),
    (19, "末小", "家道生荊棘\\n兒孫防虎威\\n香前祈福厚\\n方得免分離", "家裡的生意有阻礙，事情不按照所想地進行吧。子或孫如果常聽長輩（居上位者）的話，就會沒事吧。抱持著強烈的信心，如果竭盡真誠的心的話，將來會有好事吧。得到福德，本來別離的命運的人（物）會在不用分別的情況下解決吧。願望：能實現一半吧。疾病：雖然長期得病 ： ，但是不會危及性命吧。遺失物：大概找回不來了吧。盼望的人：變成遲遲地出現吧。蓋新居、搬家：不好也不壞吧。旅行：節制比較好吧。結婚：不會到達好的結果吧。交往：節制吧。"),
    (20, "吉", "月出漸分明\\n家財每每興\\n何言先有滯\\n更變立功名", "像是月亮也出來了，漸漸地變明朗般地，終於漸漸地希望也能被實現吧。家中的財產也能慢慢地累積，家中的生意也會繁盛起來吧。至今為止不能暢快地運作的事情，最後也會向好的方面進行吧。更進一步地，世間的評價好，變得能得到利益吧。願望：能被實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會來吧。蓋新居、搬家：好吧。結婚、交往：全部都得到好結果吧。旅行：好吧。"),
    (21, "吉", "洗出經年否\\n光華得再清\\n所求終吉利\\n重日照前程", "像是至今為止的壞事已被洗去般地，變成輕鬆暢快的狀況吧。好事再度發生，更加地帶來比現在更好的結果吧。願望都會變成好結果吧。隨著日子一天又一天的過，前途增添光輝，狀況也變好吧。願望：能被實現吧。疾病：雖然會恢復但是切忌粗心大意 ： 。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。結婚：會得到好結果吧。旅行、交往：全部好吧。"),
    (22, "吉", "漸漸濃雲散\\n看看月再明\\n逢春華菓秀\\n雨過竹重青", "像濃雲漸漸變無，萬里晴空般地，問題也解決，似乎好事會發生。像月亮再出現，於澄凈的天空放光明般地，心情也輕鬆吧。就像草木在春天生氣勃勃，花也盛開而變得色彩繽紛般地，過著充實的生活，也變得幸福吧。像竹子也遇雨增添色彩般，如果人也連連遇好事的話，越來越能得到好結果吧。願望：雖然能被實現 ： ，但是變得比較晚吧。疾病：因為會治好，耐心等待康復吧。遺失物：雖然會出現但很遲吧。盼望的人：會出現吧。蓋新居、搬家：好吧。結婚、旅行、交往：全都好吧。"),
    (23, "吉", "紅雲隨步起\\n一箭中青霄\\n鹿行千里遠\\n爭知去路遙", "已經能看到好的徵兆。要前往的將來會遇到好事吧。你也像向青空射出的箭般地作吧。這樣的話，無論什麼願望也都沒問題，會實現吧。但是受到眼前的成功的影響驕傲自大的話，就會變得看不到目標吧。通盤的判斷然後行動是很重要的吧。因為過於自信會招致失敗，小心期望過高，誠實是很重要的事。願望：雖然會實現，但是要考慮能力吧。疾病：難以康復吧。遺失物：難以找到吧。盼望的人：不能出現吧。蓋新居、搬家：好吧。結婚、交往：好吧。旅行：沒問題吧。"),
    (24, "凶", "三女莫相逢\\n盟言說未通\\n門裡心肝掛\\n縞素子重重", "產生不合道理的慾望等等的事，請不要做身為人不可以犯的錯誤行為吧。光只是口頭約束，沒有實行的話，就會與對方心意無法相通。因此，煩惱、苦悶也是不行的。抱持著信仰心吧。不這樣的話，只會發生不吉利的事吧。因此從各種面向，好好地分辨黑白是非吧。願望：不會實現吧。疾病：雖然拖很長，但會治好吧。遺失物：變成到後來才找到吧。盼望的人：不能出現吧。蓋新居、搬家：不好吧。旅行：不好吧。結婚、交往：變成不好的結果吧。"),
    (25, "吉", "枯木逢春生\\n前途必利亨\\n亦得佳人箭\\n乘車祿自行", "像草木在春天發芽，綠葉生長茂盛般地，隨著時間繁榮昌盛吧。去路必有好事發生，能幸福吧。能邂逅很棒的人吧。變得能得到崇高地位、財產吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：遲遲才來吧。蓋新居、搬家：似乎沒問題。結婚、旅行、交往：全部都變成好結果吧。"),
    (26, "吉", "將軍有異聲\\n進兵萬里程\\n爭知臨敵處\\n道勝却虛名", "平日的指導力得到部下的信賴，大家聽你的指揮吧。就像是無論在多遠的人都尊崇將軍的命令，大批士兵向前行進般地，即使多麼困難的工作都能得到身邊的人或部下的幫助吧。但是，努力急著成功都徒勞無功吧。就算是達成了目標，也會變成白費力氣吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：會變成好結果吧。"),
    (27, "吉", "望祿應重山\\n花紅喜悅顏\\n舉頭看皎月\\n漸出黑雲間", "像要越過重重相連的山脈般，因為克服辛勞又痛苦的事，沒多久就能得到上天給予的幸福吧。像紅色美麗的花朵已經綻放般的喜悅充滿臉上吧。就像如果看到月亮的話，雲也消散了，清澈地能看到般地，變成是在人生上能夠發揮能力的時期吧。就像終於從又厚又黑的雲中脫離般地，痛苦與煩惱的每天過去了，圍繞而來是沈靜安心的心情吧。但是，請多加注意，切忌粗心大意。願望：會實現吧。疾病：會治好吧，但切忌粗心大意。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：非常好吧。結婚、交往：全部都變成好結果吧。"),
    (28, "凶","意速無船渡\\n波深必誤身\\n切須回舊路\\n方可免災迍", "像是就算心裡很著急，船卻不前進般地，只是焦急，事情沒有改變吧。像是就算想勉強渡過海洋或河川，波浪又高又危險般地，就算想快點到達目的地貫徹事情，卻反而變成自己綁著自己的脖子的結果吧。想在異鄉出人頭地，不如回到故鄉靜靜地生活比較好吧。如果這樣的話，有災害也能逃離吧，自己也會變得安泰吧。願望：難以實現吧。疾病：如果長期養生的話會治好吧。遺失物：難出現吧。盼望的人：變得遲遲地才出現吧。蓋新居、搬家：壞吧。結婚、交往：壞吧。"),
    (29, "吉", "憂轗漸消融\\n求名得再通\\n寶財臨祿位\\n當遇主人公", "悲傷或擔心的事終於消失了吧。如果想聲名遠播的話，能像以前一樣再次向身邊的人傳播名聲吧。收入或地位也變成如同希望一樣實現吧。能遇到好的長官，慢慢地向成功邁進吧。願望：能被實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、當遇主人公 搬家：好吧。結婚、交往：全都好吧。"),
    (30, "半吉", "仙鶴立高枝\\n防他暗箭虧\\n井畔剛刀利\\n戶內更防危", "就算吉利的鶴想停在高高的樹枝上，沒辦法到達般地，雖有強烈的願望但阻礙很多吧。就像在黑暗的夜晚中，要難防範不知從哪飛來的箭般地，困難是能想像得到的吧。就算鶴站在泉水中，因為有又硬又銳利的刀子，似乎有危險般地，似乎要發生很多妨礙、阻礙的事吧。不單單只是外面的事，家裡的危機也是不擔心不行。願望：難實現吧。疾病：危險吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：如果能祈求神佛的保佑，會變成勉強可以的結果吧。旅行：壞吧。結婚、交往：節制吧。"),
    (31, "末吉", "鯤鯨未變時\\n且守碧潭溪\\n風雲興巨浪\\n一息過天涯", "因為鯤鯨是很大的魚，不知不覺會變成大鳥。但是，因為現在尚未變化，一直抱著很大的希望，但是還不能實現的狀態吧。就像暫時守著深青色的溪流中，等待時機的到來般地，現在天天的行動都要保守，等待幸運的到來吧。這麼做的話，時來運轉，變成大鳥的時候會到來。掀起浪花，有著向天空飛去的沸騰的心。幸運到來，朝向成功，拼命地不斷努力是很重要的。這樣做就會一口氣飛向天空吧。步向成功的道路，在世間似乎會好名聲遠播的事。 願望：雖能被實現，但要考慮時機吧。疾病：拖很久吧。遺失物：變得遲遲地才 ： 出現吧。盼望的人：變得遲遲地才出現吧。蓋新居、搬家：沒阻礙吧。旅行：好吧。結婚、交往：好吧。"),
    (32, "吉", "似玉藏深石\\n休將故眼看\\n一朝良匠別\\n方見寶光寒", "就像是不知道寶石藏深在石頭下般地，就算有才能，不在意，不努力振作施展才能的話，什麼都不能得到吧。用不管眼前事物的方式，才能是會就這樣埋沒下去吧。可是如果不斷持續地努力的話，不知不覺能被良師、益友發現。然後，就像被磨光的寶石閃閃發光地出現般，能展現成果，能為社會盡心力吧。願望：會實現吧。疾病：雖然會拖長，但是不會失去生命。遺失物：會出現吧。盼望的人：變得遲遲地才出現吧。蓋新居、搬家：好吧。結婚、交往：全部和好結果有關吧。"),
    (33, "吉", "枯木逢春艷\\n芳菲再發林\\n雲間方見月\\n前遇貴人欽", "就算是枯木也會在春天開出美麗的花朵般地，人生就算是在嚴長的冬天裡的辛勞，有一天會得到回報吧。像是草花再次盛開，氣味也充滿林間般地，幸運再次來的時節吧。像是雲散可以看見明月般地，各式各樣的困難或痛苦之間，幸運會到來吧。善人（神佛、人生的前輩）的引導，漸漸地喜事增加吧。願望：能被實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：沒有阻礙吧。旅行：好吧。結婚、交往：全都好吧。"),
    (34, "吉", "臘木春將至\\n芳菲喜再新\\n鯤鯨興巨浪\\n舉鉤祿為真", "像是冬天枯萎的樹木也會有花開的春天接近般地，人生的苦難也結束，慢慢地運氣會到來吧。像是如果春天來了的話草木也發新芽，吐芬芳，開滿花般地，能發揮才能吧。讓人看到大魚變成大鳥，掀起大波浪的氣勢，去推動事情吧。像是如果要釣魚的話就能大豐收般地，因為窮究真正的道路，你成功的時候也會到來吧。願望：能被實現吧。疾病：會治好吧。遺失物：遲遲才出現吧。盼望的人：遲吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全都和好結果相連吧。"),
    (35, "吉", "射鹿須乘箭\\n故僧引路歸\\n遇道同仙籍\\n光華映晚暉", "就像拉弓瞄準，就能按照所想地射中鹿一樣，自己的行為直接連向成功的方向吧。像被良好的引導引領般地，能得到良好的居上位者援助和意見吧。因為遵從有智慧的人的教導，能夠得到出人頭地的喜悅吧。像是花在夕陽的照耀下，越來越閃耀般地，在周圍的人對你的評價變高了吧。願望：能被實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：變遲才出現吧。蓋新居、搬家：沒有障礙吧。旅行：好吧。結婚、交往：好吧。"),
    (36, "末吉", "先損後有益\\n如月之剝蝕\\n玉兔待重生\\n光華當滿室", "即使開始的時候損失，後來一定能得到利益的，有令人高興的事吧。就算月亮變小，也會再變大，變回原來的滿月般地，雖然希望變薄弱了，但後來能被實現吧。雖然變成日食或月食的話，世界就變得黑暗，但是時間經過，馬上就回到原來的狀況。災難也隨時間過去，願望會實現吧。月亮的光芒（希望）照進家中，變得明亮般地，充滿歡喜吧。 願望：稍後會實現吧。疾病：雖然拖長，但可以治癒吧。遺失物：難出現吧。盼望的人：遲遲地才出現吧。蓋新居、搬家：應該先放棄，暫時多觀察情況再說吧。旅行：途中，似乎會有不好的事吧。結親緣、喜慶、交往：不好吧。"),
    (37, "半吉", "陰靉未能通\\n求名亦未逢\\n幸然須有變\\n一箭中雙鴻", "就像烏雲又厚又長，分不清東西般地，心裡迷惘，現在願望還無法上達天聽吧。雖然祈求名聞人世間，但是現在還沒遇到機會吧。可是心中的痛苦離去，運勢展開，變得幸福的日子會來了吧。像是用一支箭射中兩隻鳥般地，好事似乎接踵而來。願望：難以實現吧。疾病：變成遲遲地才好轉吧。遺失物：變成遲遲地才出現吧。盼望的人：變成遲遲地才出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：往後一點，變成好吧。"),
    (38, "半吉", "月照天書靜\\n雲生霧彩霞\\n久想離庭客\\n無事惹咨嗟", "像是天空沒有陰霾明顯地能看見月亮般地，沒有迷惘，澄淨的心吧。但是，至今為止看到的月亮也有雲靄，心裡也產生迷惘吧。和親密的友人分別，暫時心沈浸在悲傷的思緒中吧。雖然沒事，但是卻因為擔心悲嘆的事很多，轉換心情吧。願望：難實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：不好也不壞吧。旅行：先放棄，暫時觀察情況再說吧。結婚、交往：先放棄，暫時觀察情況吧。"),
    (39, "凶", "望用方心腹\\n家鄉被火災\\n憂危三五度\\n由損斷頭財", "就算有願望也只是心裡想想而已，還沒到達要付諸行動吧。像有家裡燒起來般地災難，接踵而來的危險。悲傷或危險的事再次地持續發生吧。因為有失去和生命一樣重要的東西的可能，要小心謹慎吧。願望：難以實現吧。疾病：又壞又危險吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋由損斷頭財 新居、搬家：避開比較好吧。旅行：不好吧。結婚、交往：招致壞結果吧。"),
    (40, "小吉", "中正方成道\\n姦邪恐惹愆\\n壺中盛妙藥\\n非久去煩煎", "正因為什麼事都不偏頗的中正之道的正確行為，能夠消除災難吧。一有邪念的話就會被引入壞的方向而去吧。就像是在藥箱中先存放著有效的藥般，不迷失去自己地珍惜真誠心吧。這樣做的話煩惱就會離去，災難會消去吧。願望：難以立刻地實現吧。疾病：雖然拖長但會治好吧。遺失物：會出現吧。盼望的人：變成遲遲才地出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：不好也不壞吧。"),
    (41, "末吉", "有物不周旋\\n須防損半邊\\n家鄉煙火裡\\n祈福始安然", "雖然有很多東西但是難到手的狀況。雖然希望很豐富，但是難以實現吧。成功一半，損失一半吧。但是不要堅持小事，想著一半已經成功事吧。有火災發生的危險。要充分地注意吧。相信神明或佛菩薩，如果抱著堅定的心，最後會變得安泰吧。願望：難以實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：變成遲遲地才出現吧。蓋新居、搬家：不好吧。旅行：途中似乎有不好的事 ： 。結婚、交往：會產生不好的結果吧。"),
    (42, "吉", "桂華春將到\\n雲天好進程\\n貴人相遇處\\n暗月再分明", "像是桂花在春天飄香般地，對你也變成是運勢展開的時機吧。人也轉運的話，有得到崇高的地位與榮譽的機會。有觀世音菩薩或有力人士的引導吧。如陰天的月亮放晴般地，越來越會發生好事吧。願望：會實現吧。疾病：會治癒吧。遺失物：會出現吧。蓋新居、搬家：好吧。盼望的人：變成遲遲地才出現吧。旅行：好吧。結婚、交往：全都會變成好結果吧。"),
    (43, "吉", "月桂將相滿\\n追鹿映山溪\\n貴人乘遠箭\\n好事始相宜", "就像月缺不久將變成滿月般地，好運全盛的時期正在接近了。鹿就是祿。也就是說，雖然現在還沒得到崇高的地位和收入，但是有將來會得到的命運。箭就是弓箭。應該要尊敬的人從遠方乘箭而來的援助之暗示是表示著如果學習這個人的善行而做的話，表示能得到崇高地位與收入。願望開始實現，名聲被好好地知道，會變得幸福吧。但是切忌高傲自滿。願望：會實現吧。疾病：雖然拖長但是會治好吧。遺失物：難出現吧。盼望的人：變成遲遲地才出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：變成好結果吧。"),
    (44, "吉", "盤中黑白子\\n一著要先機\\n天龍降甘澤\\n喜出舊根基", "就像在下圍棋當中的輸贏一樣，人生的吉或凶也還沒確定吧。勝負的事或人生都是要取得先機比什麼都還重要吧。區別善惡，如果是善道的話，筆直地著向善道而去是好的吧。神明或佛菩薩會降下甘露（恩惠）的援助吧。用甘露水洗去過去的罪惡般地，清澈地，變成可以發揮本來的能力吧。願望：會實現吧。疾病：會治癒吧。遺失物：會出現吧。盼望的人：變成遲遲地才出現吧。蓋新居、搬家：沒問題吧。旅行：好吧。結婚、交往：全都好吧。"),
    (45, "吉", "有意興高顯\\n祿馬引前程\\n得遇雲中箭\\n芝蘭滿路生", "受到別人的信賴，得到名聲，變成能夠累積財富吧。如果能一直保持著善心的話，在將來的人生幸運會成為你的嚮導吧。因為令人感謝的神佛的加護，會遇到幸運吧。如藥草或香草一片茂盛般地，被好人包圍，名聲在世間被知道，能夠變得幸福吧。願望：會實現吧。疾病：會治好吧。遺失物：遲遲地才出現吧。盼望的人：變遲遲地才出現 ：吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全都好結果相連吧。"),
    (46, "凶", "雷發震天昏\\n佳人獨掩門\\n交加文書上\\n無事也遭迍", "在烏雲裡雷聲響遍，變得像是要震撼天地般地，是非常令人擔心的狀況。少女獨自一人，沒和人交流，孤單地的狀況。要時時警戒吧。在合約等事情，似乎會發生錯誤或訴訟。雖然說如果誠心誠意地小心謹慎的話比較好，但是過度信任自己的才能，打算做什麼行動的話就全部會變成為凶。願望：難以實現吧。疾病：會治好吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：現在放棄吧。旅行：在途中有不好的事吧。結婚、交往：會產生不好的結果吧。"),
    (47, "吉", "更望身前立\\n何期在晚成\\n若遇重山去\\n財祿自相迎", "雖然為了早點實現願望似乎一直期待著，但是不可以過度著急。像是大器晚成般地，延長志氣，擴大心胸，不焦急慢慢地等待成功吧。重山是一山又一山的意思。因為辛苦地越過人生的山坡，希望也變得可以實現。必定會成功吧。財產和地位也變得可以到手吧。願望：會實現吧。疾病：變成往後才會治好吧。遺失物：會出現吧。盼望的人：變得遲遲才出現吧。蓋新居、搬家：好吧。旅行：在將來似乎有好事吧。結婚、交往：全部都可得到好 ：結果吧。"),
    (48, "小吉", "見祿隔前溪\\n勞心休更迷\\n一朝逢好渡\\n鸞鳳入雲飛", "像是隔著山谷看得見寶物般地，就算想要的東西就在眼前，似乎也難得到吧。勉強地想得到那個財寶，會使心裡迷惘，放棄吧。就這樣用平常心按照平日的生活吧。如果時機來的話，自然會得到財寶。有居上位者或認識的人的援助吧。像鳳凰飛向天空般地，會出人頭地，好事會來臨吧。 願望：如果一直抱持著正直的心的話 ： ，到後來能被實現吧。疾病：雖然拖長，但將來會治好吧。遺失物：會出現吧。盼望的人：變成遲遲才來吧。蓋新居、搬家：雖然開始不好，但是到後來會變好吧。結婚、交往、旅行：馬馬虎虎吧。"),
    (49, "吉", "正好中秋月\\n蟾蜍皎潔間\\n暗雲知何處\\n故故兩相攀", "像是十五號的夜晚，沒有月缺，又圓又明亮的月亮般地，運氣非常好吧。就像因為月亮皎潔，住在裡面的兔子和蟾蜍能清楚看見般地，展現潔淨的心和光輝吧。像是天空一點雲都沒有，萬里晴空般地，沒有妨礙的東西，心中也沒有迷惘吧。整個天空沒有雲般地，心中沒有比這個更澄淨的吧。 願望：會實現吧。疾病：嚴重吧。遺失物：難出現吧。盼望的人：變成\\n遲遲才出現吧。蓋新居、搬家：馬馬虎虎吧。旅行：好吧。結婚、交往：馬馬虎虎吧。"),
    (50, "吉", "有達宜更變\\n重山利政逢\\n前途相偶合\\n財祿保亨通", "為了達成事情，要好好地理解那件事的內容，邊改進以前的方法，邊向前進吧。如果山重疊的話，成為出這個字。已經下了使事情達成的決心的話，從現在的地方起飛展開行動吧。這麼做的話，在將來自然而然地能遇見幸福吧。再來，財寶也從一開始到結束確實地能得到吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：變遲吧。蓋新居 ： 、搬家：\\n好吧。旅行：成為好的旅行吧。結婚、交往：成為好的結果吧。"),
    (51, "吉", "修進甚功辛\\n勞生未得時\\n騰身遊碧漢\\n方得遇高枝", "雖然沒有懶惰，好像一直勤勞努力，但是現在只感覺到辛苦吧。因為有大大的願望，雖然拼命地努力，但是似乎還沒到花開的時期吧。然而，看著天空，抱著打算一飛向上的大決心，認真地挑戰看看吧。確實地能得到資產和財寶、出人頭地等，能安心吧。願望：會實現吧。疾病：變成往後才治好吧。遺失物：難出現吧。盼望的人：變晚吧。蓋新居、搬家：好吧。旅行：好事吧。結婚、交往：會得到好結果吧。"),
    (52, "凶", "有僭須惹訟\\n兼有事交加\\n門裡防人危\\n災臨莫嘆嗟", "身上發生錯誤的事，被人控訴，引起爭訟吧。這個爭訟之外，還有一件難以解開的困難爭執的事吧。原因之一是親戚或家人包含在其中，從這件事解決後，可以防止災難吧。就算有災難也不要嘆氣，幫助你的人會出現吧。願望：難實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：馬馬虎虎還算有點好吧。旅行：因為不好，避開吧。結婚、交往：不好也不壞吧。"),
    (53, "吉", "久困漸能安\\n雲書降印權\\n殘花終結實\\n時亨祿自遷", "長時間的勞苦終於溶化不見，漸漸地變好吧。從居上位者能得到好的資格（身份、或職位）或權力吧。像是殘存的花朵結成果實般地，終於運氣來了吧。變得能自由地得到福德，並且高昇，到最後都幸福吧。願望：能被實現吧。疾病：會治好吧。遺失物：變得遲遲才找到吧。盼望的人：遲遲地才出現吧。蓋新居、搬家：好吧。旅行：變成好的旅行吧。結婚、交往：全都朝向好的方向 ： 發展吧。"),
    (54, "凶", "身同意不同\\n月蝕暗長空\\n輪雖常在手\\n魚水未相逢", "只是著急，不能分出好壞吧。像月食般地，漸漸起烏雲，變得籠罩在黑暗般地狀態吧。雖然有車但是目的地沒決定般地，就算好事在眼前，也沒辦法得到的狀態吧。像是魚沒遇到水就會死亡般地，如果和周圍的人沒辦法心意相通的話，什麼是都沒辦法做成的。經常順應這個世界、心情平靜的態度是很重要的。願望：難實現吧。疾病：危險吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：暫時放棄，再觀察看看吧。結婚、交往：變成壞結果吧。"),
    (55, "吉", "雲散月重明\\n天書得誌誠\\n雖然多阻滯\\n花發再重榮", "像遮蔽月亮的雲散去，變得更加明亮般地，被關閉的心雲放晴，還變成很澄淨的心吧。像月亮或星星閃耀美麗光輝般地，人心也澄清，妨礙的事物也消失不見吧。就算有阻礙或困難，沒有到變成痛苦的程度吧。變成再度繁盛的狀態，子孫也會繁榮吧。願望：會實現吧。疾病：會治好吧。遺失物：會找到吧。盼望的人：變遲吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全都好吧。"),
    (56, "末吉", "生涯喜又憂\\n未老先白頭\\n勞心千百度\\n芳遇貴人留", "像是如果有喜事的話也會有悲傷的事般地，吉凶輪流來吧。雖然還沒到那個年齡，但長出明顯易見的白髮，是因為操心的事很多吧。會遇到好幾次重疊而來的勞苦吧。但是得到觀世音菩薩或居上位者的幫助，得到力量，最後變得幸福吧。願望：難實現吧。疾病：變成遲遲才治好吧。遺失物：會出現吧。盼望的人：遲遲才出現吧。蓋新居、搬家：半吉吧。旅行：如果有一起同行的人的話好 ： （安全）吧。結婚、交往：馬馬虎虎還可以吧。"),
    (57, "吉", "欲渡長江闊\\n波深未自儔\\n前津逢浪靜\\n重整鉤鰲鉤", "像是雖然想要渡過長長的河川，幅寬太寬難渡過般地，就算想要達成事物，困難很多吧。像是波濤凶猛、沒有船，難渡河般地，也變成達成困難的狀態吧。所以在波浪平靜、容易渡河的時候到來為止，靜靜地等待吧。一度冷靜之後，如果是準備好釣鉤的你的話，就能得到能釣大魚的契機吧。這樣得到幸運的機會會到來吧。願望：會實現吧。疾病：雖然會治好，但會拖長吧。遺失物：會出現吧。盼望的人：變遲遲才出現吧。蓋新居、搬家：好吧。旅行：壞吧。結婚、交往：馬馬虎虎還可以吧。"),
    (58, "凶", "有徑江海隔\\n車行峻嶺危\\n亦防多進退\\n猶恐小人虧", "即使有想要走的道路，就像遇到海或河的阻隔般地，要實際執行事情，有各式各樣的困難吧。像是押著車向險峻的山走去，似乎有非常大的困難。不能粗心大意。無論向前進、往後回都沒有辦法的困難的事情吧。要小心吧。有會進行阻礙的人，壞的時候，壞事接踵而來。要經常小心吧。願望：難實現吧。疾病：不能安心吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：中止吧。結婚、交往、旅行：壞吧。"),
    (59, "凶", "去住心無定\\n行藏亦未寧\\n一輪清皎潔\\n却被黑雲乘", "有飄移不定的心，沒有決定（沒有決心）吧。只是對事物迷惘，充滿各種不安吧。雖然心中的明月清澈，明亮地閃耀光輝，但被迷惘的烏雲覆蓋，僅僅一點點的未來也不能看見吧。快點除去迷惘的雲，取回原本的心吧。願望：難實現吧。疾病：危險吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：似乎會發生壞事吧。結婚、交往：得到壞結果吧。"),
    (60, "小吉", "高危安可涉\\n平坦是延年\\n守道當逢泰\\n風雲不偶然", "就像是高處的風很強般地，過於引人注目反而過得不安穩。正因為平凡的生活，才是長壽或安樂的方法。如果能守著這樣的生活方式，會是安泰又平和吧。這樣的誠實的生活必定會得到上天的恩惠吧。願望：如果正心而行的話會實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：不好吧。旅行：馬馬虎虎地算好吧。結婚、交往：馬馬虎虎地算好吧。"),
    (61, "半吉", "舊愆何日解\\n戶內保嬋娟\\n要逢十一口\\n遇鼠過牛邊", "變成擔心過去的錯誤何時才能消失吧。家裡加入美人，這件事想向世人公布就是沒有反省自己的生活與沒有節操，用心在家裡和睦吧。如果試著將十一和口重疊起來看的話，會變成吉字。也就是說，如果期望吉事而努力做的話，必定會到來吧。像是在人們沈靜入睡的夜晚也起床工作般地努力吧。願望：難實現吧。疾病：會拖長吧。遺失物：難找到吧。盼望的人：變遲吧。蓋新居、搬家：壞吧。旅行：壞吧。結婚、交往：不好吧。"),
    (62, "大吉", "災轗時時退\\n名顯四方揚\\n改故重乘祿\\n昴高福自昌", "災難也慢慢地消失，運勢會展開來吧。名聲慢慢地傳遍世間，就好的意義看，不知道的人也變得不存在吧。能改去過去的事，名聲和實際都能得到幸運吧。出人頭地，變得福運繁榮，會繁盛吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：沒問題吧。旅行：好吧。結婚、交往：全都好吧。"),
    (63, "凶", "何故生荊棘\\n佳人意漸疏\\n久困重輪下\\n黃金未出渠", "理由也一直不知道地，家中產生問題吧。家人或夫婦之間心意無法相通吧。不反省原因的話就會像被埋在重重地車輪底下般地，變得長期間地辛勞吧。因為玩樂失去財產，一直無法回復。請努力忠於自己的本分吧。願望：難實現吧。疾病：難治癒吧。遺失物：難找到吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：似乎會發生壞事吧。結婚、交往：會產生壞結果吧。"),
    (64, "凶", "安居且慮危\\n情深主別離\\n風飄波浪急\\n鴛鴦各自飛", "就算是似乎安樂，心裡也還留著憂慮吧。和感情深厚的人也有可能會發生離別的悲傷的事。這簡直是風強浪大般的狀況啊。雖然鴛鴦不分離地飛行，但是飛向分離的命運。靜靜地等待吧。願望：難實現吧。疾病：危險吧。遺失物：不會出現吧。盼望的人：不會出現吧。蓋新居、搬家：還可以吧。旅行：還可以吧。結婚、交往：不好吧。"),
    (65, "末吉", "苦病兼防辱\\n乘危亦未穌\\n若見一陽後\\n方可作良圖", "覺得內心的痛苦和受人侮辱，不安穩吧。就像面臨危險的人還沒完時甦醒般地，這個困難沒有那麼簡單地解決。如果春天來了的話（如果能有觀世音菩薩的慈悲光輝的話）也會有好事吧。從好事開始發生起，請立定計畫開始行動。到好事開始為止請靜靜地忍耐。願望：以後會實現吧。疾病：雖然拖長但會治好吧。遺失物：不會出現吧。盼望的人：變得遲遲才出現吧。蓋新居、搬家：好吧。旅行：安全吧。結婚、交往：得到還可以的 ： 好結果吧。"),
    (66, "凶", "水滯少波濤\\n飛鴻落羽毛\\n重憂心緒亂\\n閑事惹風騷", "水淤塞、浪不起可說是物質、精神貧乏、也沒有辦法從事社會活動的狀態。就像是羽毛掉落，變成無法飛行的鳥般地，失去重要的東西，沒辦法生活吧。悲傷的事接連而來，心思混亂，方法用盡不知如何是好吧。就算想待在安靜的地方，也會有引來大問題吧。願望：難實現。疾病：可疑，不明朗吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新\\n居、搬家：壞吧。旅行：壞吧。結婚、交往：壞吧。"),
    (67, "凶", "枯木未生枝\\n獨步上雲岐\\n豈知身未穩\\n獨自惹閑非", "變成枯木，枝幹上沒有長葉子，似乎現在還沒有迎接春天般地，就算要有執行不會實現的願望，心中只是越來越煩惱而已。不瞭解自己的身份、地位，就要有所行動，是無法安穩的。要有信心，要舉止謹慎吧。不悔悟自己的到前幾日為止錯誤，以後就會後悔吧。願望：難實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：多比較看看比較好吧。旅行：不好吧。結婚、交往：壞吧。"),
    (68, "吉", "異夢生英傑\\n前來事可疑\\n芳菲春日暖\\n依舊發殘枝", "生出優秀的人、做好夢是因為神佛加持庇護的幸運到來的暗示。雖然得到這個幸福，但和昨天的自身相比較，卻難以置信吧。像春天變溫暖，飄散蔬菜花的香味般地，幸福來臨。枯了的樹木也會開花般地，似乎會發生可喜可賀的事。只是，自重自愛是非常重要的。願望：會實現吧。疾病：會治好吧。遺失物：會出來吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全都好吧。"),
    (69, "凶", "明月暗雲浮\\n花紅一半枯\\n惹事傷心處\\n行舟莫遠圖", "明亮的月亮也被烏雲遮住，變為不晴朗的狀態吧。像是紅花有一半枯掉般地，運氣也變成走下坡。雖然打算努力做事，也盡是心痛、擔心吧。像要乘船等出去遠方的大希望，無法渡過般地，謹慎地等待時機到來吧。願望：難實現吧。疾病：切忌粗心大意 ： 。遺失物：難出現吧。盼望的人：不會出現吧。蓋新\\n居、搬家：壞吧。旅行：放棄吧。結婚、交往：壞吧。"),
    (70, "凶", "雷發庭前草\\n炎火向天飛\\n一心來趕祿\\n爭奈掩朱扉", "雷落在自家的庭前是由於身份低下或雇用的人引發災禍。像是火焰向天飛去般地，上下關係變得不合，有爭執吧。一心一意想要得到利益但沒辦法實現。至少要重視雇用的人或下屬等，防止災難發生吧。 願望：難實現吧。疾病：不能安心吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：避免吧。結婚、旅行、交往：萬事壞吧。"),
    (71, "凶", "道業未成時\\n何期兩不宜\\n事煩心緒亂\\n飜做徘徊思", "因為心裡和工作的實力都還沒成熟，現在是學習的時期。因為心裡和工作的實力都還沒成熟，就算想做什麼也無法按照所想地順利進行吧。因為這樣的事，引起各種麻煩，令人厭煩的痛苦和混亂吧。沒辦法好好地想事情，只是晃來晃去心情不定吧。需要反省。願望：難實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。結婚、旅行、交往：產生壞的結果吧。"),
    (72, "吉", "戶內防重厄\\n花菓見分枝\\n嚴霜纔過後\\n方可始相宜", "家中恐怕有災禍到來。但是，為了防止發生，要小心吧。枝幹各自分開是說家庭不合。因為這個緣故全部都不和睦吧。相互地悔改壞的地方，然後戰勝這的試煉。如果這樣做的話，似乎會以好事發生。因為家裡和睦，好事似乎越變越多。願望：後來會實現吧。疾病：會拖長吧。遺失物：變成遲遲才能找到吧。盼望的人：遲遲才出現吧。蓋新居、搬家：還算好吧。旅行：沒有特別的阻礙吧。結婚、交往：雖然還算好，但最後變得更好吧。"),
    (73, "吉", "久暗漸分明\\n登江綠水澄\\n芝書從遠降\\n終得異人成", "久佈烏雲的天空也終於放晴，很暢快吧。幸運似乎會到來。水或樹木都澄淨明朗，也變得沒有要擔心的事吧。因為得到居上位者的推薦，出人頭地吧。被神佛幫助，得到好結果吧。要有信心是很重要的。願望：變得往後才能被實現吧。疾病：會治好吧。遺失物：會出來吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全都好吧。"),
    (74, "凶", "蛇虎正交羅\\n牛生二尾多\\n交歲方成慶\\n上下不能和", "因為不知道蛇或虎混雜等的道理，會發生壞事。牛加上兩條尾巴的話，就變成失這個字。說不定會有什麼損失。雖然隨著年齡增加透過交流，有令人高興的事，但是卻往往常有各種爭奪、爭吵的事。因為家裡不和睦而不會平靜。用溫和的心領會忍耐吧。願望：難以實現吧。疾病：不能安心吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。結婚、旅行、交往：壞吧。"),
    (75, "凶", "孤舟欲過岸\\n浪急渡人空\\n女人立流水\\n望月意情濃", "一艘小船想要航向遙遠的對岸，會是沒有幫忙的人的狀態。因為水流急，要渡河是過度危險的事，所以是虛幻的心情。各種障礙滾滾而來，什麼事都困難的吧。柔弱的女性一人站在急流處，是非常危險的。雖然想為她作些什麼但是處於無可奈何的狀態。相對於自己的擔心，非常羨慕他人的安樂吧，但是要反省自己的行為，竭盡地拜託神佛，防止災難發生吧。願望：難實現吧。疾病：陷入的話（若是病人的話）危險吧。遺失物：不能找回來吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：壞吧。結婚、交往：壞吧。"),
    (76, "吉", "富貴天之祐\\n何須苦用心\\n前程應顯跡\\n久用得高臨", "得到財產、地位變高是上天賜給的東西。就算用盡心思與痛苦，沒有神佛的幫忙的話，不能實現吧。前程的好壞是根據至今為止所做的行為的好壞而來的吧。長時間實行正道、徹底行善等等的話，地位會變高，財寶也能得到吧。願望：會實現吧。疾病：會治好吧。遺失物：會出來吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全部都好吧。"),
    (77, "凶", "累滯未能穌\\n求名莫遠圖\\n登舟波浪急\\n咫尺隔天衢", "萬事不能順利進行會接連而來，看不到前景吧。現在不能想要名聲廣播、祈求幸福等。想要乘船而去，但浪高難以渡過吧。雖然願望好像快要實現，但是被災難阻擋。結果的差別像天和地般地不一樣的狀況。請自重，等待時機的到來吧。願望：難實現吧。疾病：不能安心吧。遺失物：難找到吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：壞吧。結婚、交往：壞吧。"),
    (78, "大吉", "但存公道正\\n何愁理去忠\\n松柏蒼蒼翠\\n前山祿馬重", "守著公共的正道，比起為了自己，更要為了大家做好事吧。忠實地盡心盡力做事，就算這樣反而事情不能順利進行、立場變壞也要當作沒有悲傷嘆息的事吧。就像松樹或柏樹經常青翠般地，人的心也要注意要經常走在誠懇的道路吧。到最後會有好事，福德像是滿出來般地變得幸福吧。願望：會實現吧。疾病：會治好吧。遺失物：會出來吧。盼望的人：會出現吧。蓋新居、搬\\n家：好吧。旅行：好吧。結婚、交往：全都好吧。"),
    (79, "吉", "殘月未還光\\n樽前非語傷\\n戶中有人厄\\n祈福保青陽", "像是明亮的月光還沒衰退、光輝閃耀著般地，你也隨著上年紀越來越能活躍。就像是就算喝酒，一點點也不會混亂般地，什麼壞事都沒做，但是，家中稍微有災難吧。如果懷著信心，期禱幸福的話，像是溫暖的日光照射的春天般地，心變得安定、安泰吧。願望：雖然能被實現但是大願望不行吧。疾病：雖然會拖長，但會治好吧。遺失物：遲遲地才找到吧。盼望的人：變遲才出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：好吧。"),
    (80, "大吉", "深山多養道\\n忠正帝王宣\\n鳳遂鸞飛去\\n昇高過九天", "險惡的修行是要窮究真誠之道吧。忠誠的心被認同、居上位者派人過來，變成大大地出人頭地吧。鳳凰也是鸞也是，是出現在正確的人世間的鳥。是可喜可賀的象徵。飛越極高的天空，還登上比這樣更高吧。因為努力，高高的目標陸陸續續地能達成吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：是好的，因為全部都保持謙虛的姿態，所以會招來好結果吧。"),
    (81, "小吉", "道合須成合\\n先憂事更多\\n所求財寶盛\\n更變得中和", "如果自身的行為符合道理的話，什麼都會成功吧。但是在最初的時候悲傷和痛苦會很多吧。之後，所希望的財寶會如心想地聚集過來吧。未來的災難也會馬上變成往幸福的方向，繁盛會到來吧。願望：如果保持端正的心的話 ： ，會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：好吧。"),
    (82, "凶", "火發應連天\\n新愁惹舊愆\\n欲求千里外\\n要渡更無船", "有天井也燒焦般的大火是因為慾望或怒氣而不能安穩的意思。新的悲傷或痛苦、然後舊傷痕等被拿出來，令人擔心的事很多吧。就算想逃到遠處但是相當地困難吧。前往的目的地有大河，就算想渡河而過但沒有船會相當辛苦。暫時保持現狀吧。願望：難實現吧。疾病：可疑，不明朗吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：多比較看看比較好吧。結婚、交往：全都壞吧。"),
    (83, "凶", "舉步出雲端\\n高枝未可攀\\n昇頭看皎月\\n猶在黑雲間", "想抬腳乘雲登天，卻不能登天。高高的願望是沒有用的事。想爬上高高的樹枝，但是抓得到的樹枝，像是沒有比這個更高的一樣，自己的生活不安，也沒有援助吧。抬頭看天空，就算想看見晴朗的月亮，自己想看的月亮還隱藏在雲中，不能好好看見。安靜地端正行為吧。願望：難實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：危險吧。結婚、交往：產生壞結果吧。"),
    (84, "凶", "否極方無泰\\n花開值晚秋\\n人情不調備\\n財寶鬼來偷", "八方堵塞，沒有暢通的道路吧。雖然花會開但是受晚秋般地冷風吹拂，立刻就枯萎了吧。各自為了自己的主張，人情心也不一致，抱怨不停吧。儲存的寶物或財產也因魔鬼出現偷走，財產漸漸地減少，於是變得貧窮吧。願望：難實現吧。疾病：危險吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：不好吧。結婚、交往：全部都產生壞的結果吧。"),
    (85, "大吉", "望用何愁晚\\n求名漸得寧\\n雲梯終有望\\n歸路入蓬瀛", "雖說願望很晚才會實現，不悲傷嘆息慢慢地等待吧。漸漸地名聲揚起，變成安心的心情吧。大大的願望也得到援助，終於能被實現吧。變成能得到福德、財產、長壽吧。願望：變成往後才會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：好吧。"),
    (86, "大吉", "花發應陽臺\\n車行進寶財\\n執文朝帝殿\\n走馬聽聲雷", "像是從照到陽光的房屋，可以充分地看見花盛開的景象般地，一切都能如願地充分被能實現吧。像是堆滿財寶的車子來到自己的家般地，財產或寶物變得豐富吧。顯現學問的德行，被居上位者帶領，還讓你能說出願望吧。得意洋洋地騎馬，那種姿態是變成成令人羨慕的身份吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全都好吧。"),
    (87, "大吉", "鑿石方逢玉\\n淘沙始見金\\n青霄終有路\\n只恐不堅心", "偶然挖出石頭中的寶石可說是遇見沒想過的幸福。就像是淘砂收集金子般地，在生活中財寶自然地累積吧。想向天空實現大成功之道，在世間也廣為稱讚吧。只是，如果不意志堅定一心努力的話，什麼是都不能成功吧。願望：能被實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。結婚、交往：好吧。"),
    (88, "凶", "作事不和同\\n臨危更主凶\\n佳人生苦根\\n閑慮兩三重", "就算想做些什麼事，卻和人或者夫婦之間是不和睦的狀態。因為在這樣的狀態下，就算想從危險的事逃離、防止危險的事，壞事還是發生吧。產生像是關係到自己的妻子般的痛苦或擔心的事。壞事一而再再而三地接踵發生。要非常有信心吧。願望：難實現吧。疾病：危險吧。遺失物：不會出現吧。盼望的人：不會出現吧。蓋新居、\\n搬家：壞吧。旅行：壞吧。結婚、交往：壞吧。"),
    (89, "大吉", "一片無瑕玉\\n從今好琢磨\\n得遇高人識\\n方逢喜氣多", "玉石因為琢磨終於變成無瑕疵的玉是世上天賜給的東西。就像天生的好人也因雕琢的方式不同變成更好的人般地，誠心地更加努力吧。這樣做的話會被名聲高的人賞識，變成能得到提拔吧。智慧或財寶充滿，被無限的欣喜包圍的時機會機到來吧。願望：能被實現吧。疾病：會治好吧。遺失物：不會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：好吧。"),
    (90, "大吉", "一信向天飛\\n秦川舟自歸\\n前途成好事\\n應得貴人推", "如果有真誠心的話，最後會傳達給上天，出人頭地的時候會到來吧。因為上天的恩惠，會得到各種財寶吧。將來會遇見好事吧。因為得到居上位者（菩薩）的力量，能被吸引往好的方向吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬\\n家：好吧。旅行：好吧。結婚、交往：全部都好吧。"),
    (91, "吉", "改變前途去\\n月桂又逢圓\\n雲中乘祿至\\n凡事可宜先", "如果改進到現在為止壞事，嶄新地向前進的話，事情會改變的吧。就像缺月也會再變圓般地，吉事就猶如月的圓缺。至今為止的缺點也會漸漸地變好吧。從天降下來福德、幸運吧。在做任何事時，也不要落於人後，先做就能得到好結果吧。願望：如果守正道的話會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：好吧。"),
    (92, "吉", "自幼常為旅\\n逢春駿馬驕\\n前程宜進步\\n得箭降青霄", "從小時候起的到流落旅行就是內心的不安定，勞苦很多。如果變成春天的話，就像馬也振奮地來回奔跑般底，終於運氣到來吧。就算如心想地去了哪裡，會變成如自己想的一樣吧。箭筆直地向前進時是要射中獵物。從天而來的幸運向你而來吧。願望：會實現吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：好吧。"),
    (93, "吉", "有魚臨旱池\\n跳躍入波濤\\n隔中須有望\\n先且慮塵勞", "雖然有很多魚但是池子裡如果沒有水會死掉吧。如果沒有保持著真誠心的話，人總有一天會向滅絕而去吧。就像是在沒水池子裡的魚如果進入廣大的河川的話，也生氣勃勃般地，你的運勢也終於到來了吧。但是因為有阻礙，要十分注意吧。暫時忍耐吧。因為忍耐，來生、後世或子孫能幸福吧。願望：變成到後來能實現吧。疾病：會拖長吧。遺失物：難出現吧。盼望的人：變遲吧。蓋新居、搬家：馬馬虎虎還算可以吧。旅行：好吧。結婚、交往：好吧。"),
    (94, "半吉", "事忌樽語\\n人防小輩交\\n幸乞陰公祐\\n方免事敵爻", "喝酒時說的話是邊喝酒邊說出的話，不能全部當真。避免和比自己低下的人交流吧。應該要避免只說場面話吧。好好遵從母親（神、佛）吧。如果這樣做的話，願望能被實現吧。化解對事物的敵對意識，廣泛和人交往吧。漸漸地會變成幸福吧。願望：不能按照所想的實現吧。疾病：雖然會拖長但是不會危害生命吧。要特別用心維持健康吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：不好吧。旅行：馬馬虎虎還算可以吧。結婚、交往：勉強還算可以吧。"),
    (95, "吉", "志氣勤修業\\n祿位未造逢\\n若聞金雞語\\n乘船得便風", "立定志向，如果一心努力的話，漸漸地會朝向好的方向吧。現在就算福運還沒到來，必定之後會到來吧。就像等待著黑夜放明，雞開始啼叫般地，等待時機的到來吧。時機到來、就像風把船推向前進的方向般地，漸漸地朝向幸福的方向吧。願望：能被實現吧。疾病：變成遲遲才治好吧。遺失物：變成遲遲地才出現吧。盼望的人：遲遲地才出現吧。蓋新居、搬家：沒有阻礙吧。旅行：好吧。結婚、交往：好吧。"),
    (96, "大吉", "雞逐鳳同飛\\n高林整羽儀\\n棹舟須濟岸\\n寶貨滿船歸", "就像雞一邊追著鳳凰，也和鳳凰一樣地飛翔般地，仰賴有地位的人，出人頭地吧。然後，就像停在高高的樹林，整理羽毛般地，在和身份高的人交流中能得到幸福吧。就像船撐篙要渡向對岸一般地，因為自己開始行動，在世間能安心地渡過吧。出人頭地，就像財寶也很多，堆滿船歸來般地，約定了幸福。願望：能被實現吧。但是，抱持全面謹慎的心是很重要的。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：全部好吧。"),
    (97, "凶", "霧罩重樓屋\\n佳人水上行\\n白雲歸去路\\n不見月波澄", "就像高高房子也隱於霧中看不見般地，煩惱的事不斷，每天昏暗、陰天吧。就像柔弱的女性獨自一人乘船在水上旅行般地，現在正面臨危險的狀態。白雲未定，去的方向也不知道。每天不知道會發生什麼事吧。就像澄清的水應該映著月亮的倒影也因為波浪凶猛看不見般地，種種妨礙很多吧。首先要內心安定是很重要的。願望：難以實現吧。疾病：危險吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：不好吧。結婚、交往：壞吧。"),
    (98, "凶", "欲理新絲亂\\n閑愁足是非\\n只困羅網裡\\n相見幾人悲", "就像想回復糾纏在一起混亂的絲線是困難的般地，想要除去心中的痛苦是苦難吧。獨自靜靜地抱著很多煩惱或悲傷，就連事物的善惡也以難發現吧。就像魚被困在網中身體不能動般地，掙扎會感到痛苦吧。自己還有身邊的人也悲傷、煩惱的事很多，接踵不斷吧。然而如果用信心的去作話，能逃離吧。願望：難以實現吧。疾病：可疑，不明朗 ： 吧。遺失物：難出現吧。盼望的人：不會出現吧。蓋新居、搬家：壞吧。旅行：壞吧。結婚、交往：壞吧。"),
    (99, "大吉", "紅日當門照\\n暗月再重圓\\n遇珍須得寶\\n頗有稱心田", "就像朝陽閃耀照在門前，變得明亮般地，有因上天的恩惠而來的好事吧。到現在為止的黑夜中月亮再度變成滿月，普照四周吧。開朗的心情會讓周遭和睦、平靜吧。能得到稀奇的財寶吧。變得有名，變成心願實現吧。要小心謹慎粗心大意和驕傲的事。願望：能被實現吧。在萬事中要用謙虛的心吧。疾病：會治好吧。遺失物：會出現吧。盼望的人：會出現吧。蓋新居、搬家：好吧。旅行：好吧。結婚、交往：好吧。"),
    (100, "凶", "祿走白雲間\\n攜琴走遠山\\n不遇神仙面\\n空惹意闌珊", "幸福的事也隱藏在雲中而失去，是失去倚賴吧。拿著琴走往山中的樣子是表示捨去人世的意思。在走往山中的途中，沒有遇到仙人傳授道理，心中不安吧。心中空虛、發呆，方法用盡不知如何是好吧。更換心情，不要抱著太大的野心地在人世間過生活吧。願望：難實現吧。疾病：危險吧。遺失物：難出現吧。盼望的人：壞吧。蓋新居、搬家：壞吧。旅行：壞吧。結婚、交往：全部壞吧。")
]


for p in POETRIES:
  print("""
      "Poetry%(index)d": {
        "name": "Poetry%(index)d",
        "expect_input": false,
        "next_node_id": "PoetryRouter%(index)d",
        "module": {
          "id": "ai.compose.content.core.message",
          "config": {
            "messages": [
              {
                "text": "【%(type)s】\\n%(poetry)s"
              }
            ],
            "quick_replies": [
              {
                "content_type": "text",
                "title": "老師解說"
              },
              {
                "content_type": "text",
                "title": "再抽一次"
              }
            ]
          }
        }
      },
      "PoetryRouter%(index)d": {
        "name": "PoetryRouter%(index)d",
        "expect_input": true,
        "next_node_id": "Root",
        "module": {
          "id": "ai.compose.router.core.default",
          "config": {
            "links": [
              {
                "rule": {
                  "type": "regexp",
                  "params": ["說明", "解說"]
                },
                "end_node_id": "PoetryExplain%(index)d",
                "ack_message": ""
              }
            ],
            "on_error": {
              "end_node_id": "Root",
              "ack_message": ""
            }
          }
        }
      },
      "PoetryExplain%(index)d": {
        "name": "Poetry%(index)d",
        "expect_input": false,
        "next_node_id": "RootRouter",
        "module": {
          "id": "ai.compose.content.core.message",
          "config": {
            "messages": [
              {
                "text": "%(explain)s"
              }
            ],
            "quick_replies": [
              {
                "content_type": "text",
                "title": "再抽一次"
              }
            ]
          }
        }
      },
""" % {
        'index': p[0],
        'type': p[1],
        'poetry': p[2],
        'explain': p[3]
    })
