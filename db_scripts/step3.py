counts = []
totals = {}
print "delete from map_data;"
for line in file('step2.txt'):
    if len(line.split('|')) == 1:
        if not counts:
            question_id = int(line)
            counts = []
            continue
        counts = [int((int(x[0]) / float(totals[int(x[1])])) * 10000) / 100.0 for x in counts]
        x1 = counts[len(counts) / 3]
        x2 = counts[2 * len(counts) / 3]
        print "insert into map_data (question_id, rng1_num, rng1, rng2_num, rng2, rng3_num, rng3) values (%s, %s, \"%s\", %s, \"%s\", %s, \"%s\");" % (question_id, x1, "%02.2f %%" % x1, x2, "%02.2f %%" % x2, 100, "100 %")
        question_id = int(line)
        counts = []
    elif len(line.split('|')) == 2:
        counts.append(line.split('|'))
    else:
        total, country, ignore = [int(x) for x in line.split('|')]
        totals[country] = total
