from tasks import splitTags

source = {"content": "111", "title_cn": "", "summary": "333", "tags": "444", "read_num": "555"}

if 'title_cn' not in source:
    print("err1")
else:
    print(source['title_cn'])




def joinContent(contents):
    result = []
    for content in contents:
        if (content.startswith('<image') or content.startswith('<table')) and content.endswith('>'):
            continue
        else:
            result.append(content)
    return ''.join(result)

ret = joinContent([
        "据德国新闻电视频道网站5月10日报道，俄罗斯前总统、现任俄罗斯联邦安全会议副主席梅德韦杰夫威胁伦敦和巴黎说，如果乌克兰使用英国或法国巡航导弹袭击俄罗斯，俄就将发起猛烈反击。梅德韦杰夫在“电报”软件上写道，主导这类对俄罗斯领土袭击的不会是“穿着绣花衣的白痴，而是英国人和法国人”。他用“绣花衣”暗指乌克兰人的传统服装。\n",
        "\n",
        "<image1>",
        "图为英法两国向乌克兰提供的“风暴阴影”巡航导弹\n",
        "报道称，梅德韦杰夫进一步威胁说，对此类巡航导弹袭击的回应“在某些情况下”不会是只针对基辅的，“而且不仅使用常规炸药，也会使用特种弹药。”他就英国说，英国国王手下那些“没有受过充分训练的白痴”也应该明白这一点。\n",
        "报道还称，自俄罗斯对乌克兰发动军事行动以来，梅德韦杰夫对西方发出的威胁一次比一次严厉。\n",
        "法国和英国都向乌克兰提供了巡航导弹。但德国总理朔尔茨一直拒绝向乌克兰提供这种武器。\n",
        "另据路透社5月10日报道，梅德韦杰夫10日说，俄罗斯计划举行的核演习的目的是确定如何应对西方允许乌克兰使用其提供的武器对俄罗斯领土发动的任何袭击。\n",
        "梅德韦杰夫在“电报”软件上写道：“在特定情况下，（对此类袭击的）回应将不光针对基辅。而且不仅有常规爆炸物，还有一种特殊武器。”\n"
    ])
print(len(ret))
