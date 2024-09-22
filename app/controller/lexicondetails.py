field_list = ['lexemeId',
              'headword',
            #   'Sense.Grammatical Category',
              'Sense.Gloss.eng',
              'Sense.Gloss.hin',
              'Sense.Gloss.san',
              'Sense.Gloss.mai']
def get_all_lexicon_details(lexemes, activeprojectname, field_list=field_list):
    get_fields = get_mongo_output_dict(field_list)
    # print('Get fields', get_fields)
    if 'SenseNew' in get_fields:
        sense_subfields = get_relevant_subfields('Sense', field_list)
        # print('Sense fields', sense_subfields)
    elif 'Variant' in get_fields:
        variant_subfields = get_relevant_subfields('Variant', field_list)
        # print('Variant fields', variant_subfields)

    details = []
    added_fields = []

    all_lexemes = lexemes.find({'projectname': activeprojectname, 'lexemedeleteFLAG': 0},
                               get_fields)
    for current_lexeme in all_lexemes:
        # print(len(current_lexeme), current_lexeme)
        current_lexeme_details = {}
        if (len(current_lexeme['headword']) != 0):
            for lexeme_field in current_lexeme:
                if 'SenseNew' in lexeme_field:
                    sense_all_details = append_with_subfields(
                        current_lexeme[lexeme_field], sense_subfields, added_fields)
                    # print('Sense all details', sense_all_details)
                    current_lexeme_details.update(sense_all_details)
                elif 'Variant' in lexeme_field:
                    variant_all_details = append_with_subfields(
                        current_lexeme[lexeme_field], variant_subfields, added_fields)
                    current_lexeme_details.update(variant_all_details)
                else:
                    field_all_details = append_single(
                        current_lexeme[lexeme_field], lexeme_field, added_fields)
                    current_lexeme_details.update(field_all_details)

            details.append(current_lexeme_details)
    # print(details)
    # print(added_fields)
    added_fields = clean_added_fields(added_fields)
    # print(added_fields)
    return added_fields, details


def clean_added_fields(added_fields):
    cleaned_fields = []
    for current_field in added_fields:
        if current_field not in cleaned_fields:
            if current_field == 'lexemeId':
                cleaned_fields.insert(0, current_field)
            elif current_field == 'headword':
                cleaned_fields.insert(1, current_field)
            else:
                cleaned_fields.append(current_field)
    return cleaned_fields


def append_single(lexeme_field_value, lexeme_field, added_fields):
    all_field_details = {}
    if lexeme_field_value in all_field_details:
        all_field_details[lexeme_field].append(
            lexeme_field_value)
    else:
        all_field_details[lexeme_field] = [lexeme_field_value]

    if lexeme_field not in added_fields:
        added_fields.append(lexeme_field)

    return all_field_details


def append_with_subfields(lexeme_field, subfields_dict, added_fields):
    all_field_details = {}
    # print('lexeme_field', lexeme_field)
    # print('All field details', all_field_details)
    # print('Current field,', lexeme_field)
    for current_entry_key, current_entry in lexeme_field.items():
        # print('Current Sense', current_entry_key, current_entry)
        for field_subfield, fieldsubsubfield in subfields_dict.items():
            # print('Field subfield', field_subfield)
            # print('Subfield dict', subfields_dict)
            if field_subfield in current_entry:
                if len(fieldsubsubfield) == 1:
                    if field_subfield == fieldsubsubfield[0]:
                        if field_subfield in all_field_details:
                            all_field_details[field_subfield].append(
                                current_entry[field_subfield])
                        else:
                            all_field_details[field_subfield] = [
                                current_entry[field_subfield]]

                        if field_subfield not in added_fields:
                            added_fields.append(field_subfield)

                else:
                    # for fieldsubsubkey in fieldsubsubfield:
                    #     field_name = field_subfield+'(' + fieldsubsubkey + ')'
                    #     if len(all_field_details[field_name]) != 0:
                    #         del all_field_details[field_name]

                    for fieldsubsubkey in fieldsubsubfield:
                        # print('All field details',
                        #   fieldsubsubkey, all_field_details)
                        field_name = field_subfield+'(' + fieldsubsubkey + ')'

                        if fieldsubsubkey in current_entry[field_subfield]:
                            subsubfieldval = current_entry[field_subfield][fieldsubsubkey]
                        else:
                            subsubfieldval = ''

                        if field_name in all_field_details:
                            all_field_details[field_name].append(
                                subsubfieldval)
                        else:
                            all_field_details[field_name] = [subsubfieldval]

                        if field_subfield not in added_fields:
                            added_fields.append(field_name)
                        # print('All field details',
                        #       fieldsubsubkey, all_field_details)
            else:
                subfieldval = ''
                # print('All field details not found', all_field_details)
                if field_subfield in all_field_details:
                    all_field_details[field_subfield].append(
                        subfieldval)
                else:
                    all_field_details[field_subfield] = [
                        subfieldval]

                if field_subfield not in added_fields:
                    added_fields.append(field_subfield)
                # print('All field details', fieldsubsubkey, all_field_details)

    # print('All field details returned', all_field_details)
    return all_field_details


def get_mongo_output_dict(field_list):
    mongo_dict = {'_id': 0}
    for current_field in field_list:
        if 'Sense' in current_field:
            mongo_dict['SenseNew'] = 1
        elif 'Variant' in current_field:
            mongo_dict['Variant'] = 1
        else:
            mongo_dict[current_field] = 1

    return mongo_dict


def get_relevant_subfields(parent_field, field_list):
    subfields = {}
    for field in field_list:
        if field.startswith(parent_field):
            subfield = field[field.find('.')+1:]
            if '.' in subfield:
                inner_subfield = subfield[subfield.find('.')+1:]
                subfield_parent = subfield[:subfield.find('.')]
                if subfield_parent in subfields:
                    subfields[subfield_parent].append(inner_subfield)
                else:
                    subfields[subfield_parent] = [inner_subfield]
            else:
                if parent_field in subfields:
                    subfields[subfield].append(subfield)
                else:
                    subfields[subfield] = [subfield]
    return subfields
