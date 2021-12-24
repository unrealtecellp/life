var morphType = [
                      {"id": "lemma", "text": "lemma"},
                      {"id": "wordform", "text": "wordform"},
                      {"id": "affix", "text": "affix"},
                      {"id": "clitic", "text": "clitic"}
                    ]

var morphemicGloss = [
                {
                  "text": "ModificationType",
                  "children": 
                  [
                    {"id": "indifferent", "text": "indifferent"},
                    {"id": "postModifier", "text": "postModifier"},
                    {"id": "preModifier", "text": "preModifier"}  
                  ]
                },
                  {
                    "text": "Number",
                    "children": 
                    [
                      {"id": "collective", "text": "collective"},
                      {"id": "dual", "text": "dual"},
                      {"id": "massNoun", "text": "massNoun"},
                      {"id": "otherNumber", "text": "otherNumber"},
                      {"id": "paucal", "text": "paucal"},
                      {"id": "plural", "text": "plural"},
                      {"id": "quadrial", "text": "quadrial"},
                      {"id": "singular", "text": "singular"},
                      {"id": "trial", "text": "trial"}
                    ]
                  },
                {
                  "text": "Animacy",
                  "children": 
                  [
                    {"id": "animate", "text": "animate"},
                    {"id": "inanimate", "text": "inanimate"},
                    {"id": "otherAnimacy", "text": "otherAnimacy"}
                  ]
                },
                {
                  "text": "TermType",
                  "children": 
                  [
                    {"id": "CJK_compound", "text": "CJK_compound"},
                    {"id": "abbreviatedForm", "text": "abbreviatedForm"},
                    {"id": "abbreviation", "text": "abbreviation"},
                    {"id": "acronym", "text": "acronym"},
                    {"id": "appellation", "text": "appellation"},
                    {"id": "clippedTerm", "text": "clippedTerm"},
                    {"id": "commonName", "text": "commonName"},
                    {"id": "compound", "text": "compound"},
                    {"id": "contraction", "text": "contraction"},
                    {"id": "entryTerm", "text": "entryTerm"},
                    {"id": "equation", "text": "equation"},
                    {"id": "expression", "text": "expression"},
                    {"id": "formula", "text": "formula"},
                    {"id": "fullForm", "text": "fullForm"},
                    {"id": "idiom", "text": "idiom"},
                    {"id": "initialism", "text": "initialism"},
                    {"id": "internationalScientificTerm", "text": "internationalScientificTerm"},
                    {"id": "internationalism", "text": "internationalism"},
                    {"id": "logicalExpression", "text": "logicalExpression"},
                    {"id": "nucleus", "text": "nucleus"},
                    {"id": "partNumber", "text": "partNumber"},
                    {"id": "phraseologicalUnit", "text": "phraseologicalUnit"},
                    {"id": "productName", "text": "productName"},
                    {"id": "proverb", "text": "proverb"},
                    {"id": "setPhrase", "text": "setPhrase"},
                    {"id": "shortForm", "text": "shortForm"},
                    {"id": "sku", "text": "sku"},
                    {"id": "standardText", "text": "standardText"},
                    {"id": "string", "text": "string"},
                    {"id": "stringCategory", "text": "stringCategory"},
                    {"id": "symbol", "text": "symbol"},
                    {"id": "transcribedForm", "text": "transcribedForm"}
                  ]
                },
                {
                  "text": "VerbFormMood",
                  "children": 
                  [
                    {"id": "conditional", "text": "conditional"},
                    {"id": "gerundive", "text": "gerundive"},
                    {"id": "imperative", "text": "imperative"},
                    {"id": "indicative", "text": "indicative"},
                    {"id": "infinitive", "text": "infinitive"},
                    {"id": "participle", "text": "participle"},
                    {"id": "subjunctive", "text": "subjunctive"}
                  ]
                },
                {
                  "text": "NormativeAuthorization",
                  "children": 
                  [
                    {"id": "admittedTerm", "text": "admittedTerm"},
                    {"id": "deprecatedTerm", "text": "deprecatedTerm"},
                    {"id": "legalTerm", "text": "legalTerm"},
                    {"id": "preferredTerm", "text": "preferredTerm"},
                    {"id": "regulatedTerm", "text": "regulatedTerm"},
                    {"id": "standardizedTerm", "text": "standardizedTerm"},
                    {"id": "supersededTerm", "text": "supersededTerm"}
                  ]
                },
                {
                  "text": "Person",
                  "children": 
                  [
                    {"id": "firstPerson", "text": "firstPerson"},
                    {"id": "secondPerson", "text": "secondPerson"},
                    {"id": "thirdPerson", "text": "thirdPerson"}
                  ]
                },
                {
                  "text": "Degree",
                  "children": 
                  [
                    {"id": "comparative", "text": "comparative"},
                    {"id": "positive", "text": "positive"},
                    {"id": "superlative", "text": "superlative"}
                  ]
                },
                {
                  "text": "Dating",
                  "children": 
                  [
                    {"id": "modern", "text": "modern"},
                    {"id": "old", "text": "old"}
                  ]
                },
                {
                  "text": "Gender",
                  "children": 
                  [
                    {"id": "commonGender", "text": "commonGender"},
                    {"id": "feminine", "text": "feminine"},
                    {"id": "masculine", "text": "masculine"},
                    {"id": "neuter", "text": "neuter"},
                    {"id": "otherGender", "text": "otherGender"}
                  ]
                },
                {
                  "text": "Cliticness",
                  "children": 
                  [
                    {"id": "bound", "text": "bound"},
                    {"id": "no", "text": "no"},
                    {"id": "yes", "text": "yes"}
                  ]
                },
                {
                  "text": "Frequency",
                  "children": 
                  [
                    {"id": "commonlyUsed", "text": "commonlyUsed"},
                    {"id": "infrequentlyUsed", "text": "infrequentlyUsed"},
                    {"id": "rarelyUsed", "text": "rarelyUsed"}
                  ]
                },
                {
                  "text": "TermElement",
                  "children": 
                  [
                    {"id": "affix", "text": "affix"},
                    {"id": "baseElement", "text": "baseElement"},
                    {"id": "infix", "text": "infix"},
                    {"id": "inflectionElement", "text": "inflectionElement"},
                    {"id": "morphologicalElement", "text": "morphologicalElement"},
                    {"id": "optionalElement", "text": "optionalElement"},
                    {"id": "prefix", "text": "prefix"},
                    {"id": "radical", "text": "radical"},
                    {"id": "suffix", "text": "suffix"},
                    {"id": "syllable", "text": "syllable"},
                    {"id": "wordElement", "text": "wordElement"}
                  ]
                },
                {
                  "text": "Negative",
                  "children": 
                  [
                    {"id": "no", "text": "no"},
                    {"id": "yes", "text": "yes"}
                  ]
                },
                {
                  "text": "ReferentType",
                  "children": 
                  [
                    {"id": "personal", "text": "personal"},
                    {"id": "possessive", "text": "possessive"}
                  ]
                },
                {
                  "text": "Finiteness",
                  "children": 
                  [
                    {"id": "finite", "text": "finite"},
                    {"id": "nonFinite", "text": "nonFinite"}
                  ]
                },
                {
                  "text": "Voice",
                  "children": 
                  [
                    {"id": "activeVoice", "text": "activeVoice"},
                    {"id": "middleVoice", "text": "middleVoice"},
                    {"id": "passiveVoice", "text": "passiveVoice"}
                  ]
                },
                {
                  "text": "Definiteness",
                  "children": 
                  [
                    {"id": "definite", "text": "definite"},
                    {"id": "fullArticle", "text": "fullArticle"},
                    {"id": "indefinite", "text": "indefinite"},
                    {"id": "shortArticle", "text": "shortArticle"}
                  ]
                },
                {
                  "text": "Tense",
                  "children": 
                  [
                    {"id": "future", "text": "future"},
                    {"id": "imperfect", "text": "imperfect"},
                    {"id": "past", "text": "past"},
                    {"id": "present", "text": "present"},
                    {"id": "preterite", "text": "preterite"}
                  ]
                },
                {
                  "text": "Mood",
                  "children": 
                  [
                    {"id": "imperative", "text": "imperative"},
                    {"id": "indicative", "text": "indicative"},
                    {"id": "subjunctive", "text": "subjunctive"}
                  ]
                },
                {
                  "text": "Register",
                  "children": 
                  [
                    {"id": "benchLevelRegister", "text": "benchLevelRegister"},
                    {"id": "dialectRegister", "text": "dialectRegister"},
                    {"id": "facetiousRegister", "text": "facetiousRegister"},
                    {"id": "formalRegister", "text": "formalRegister"},
                    {"id": "inHouseRegister", "text": "inHouseRegister"},
                    {"id": "ironicRegister", "text": "ironicRegister"},
                    {"id": "neutralRegister", "text": "neutralRegister"},
                    {"id": "slangRegister", "text": "slangRegister"},
                    {"id": "tabooRegister", "text": "tabooRegister"},
                    {"id": "technicalRegister", "text": "technicalRegister"},
                    {"id": "vulgarRegister", "text": "vulgarRegister"}
                  ]
                },
                {
                  "text": "Case",
                  "children": 
                  [
                    {"id": "abessiveCase", "text": "abessiveCase"},
                    {"id": "ablativeCase", "text": "ablativeCase"},
                    {"id": "absolutiveCase", "text": "absolutiveCase"},
                    {"id": "accusativeCase", "text": "accusativeCase"},
                    {"id": "adessiveCase", "text": "adessiveCase"},
                    {"id": "aditiveCase", "text": "aditiveCase"},
                    {"id": "allativeCase", "text": "allativeCase"},
                    {"id": "benefactiveCase", "text": "benefactiveCase"},
                    {"id": "causativeCase", "text": "causativeCase"},
                    {"id": "comitativeCase", "text": "comitativeCase"},
                    {"id": "dativeCase", "text": "dativeCase"},
                    {"id": "delativeCase", "text": "delativeCase"},
                    {"id": "elativeCase", "text": "elativeCase"},
                    {"id": "equativeCase", "text": "equativeCase"},
                    {"id": "ergativeCase", "text": "ergativeCase"},
                    {"id": "essiveCase", "text": "essiveCase"},
                    {"id": "genitiveCase", "text": "genitiveCase"},
                    {"id": "illativeCase", "text": "illativeCase"},
                    {"id": "inessiveCase", "text": "inessiveCase"},
                    {"id": "instrumentalCase", "text": "instrumentalCase"},
                    {"id": "lativeCase", "text": "lativeCase"},
                    {"id": "locativeCase", "text": "locativeCase"},
                    {"id": "nominativeCase", "text": "nominativeCase"},
                    {"id": "obliqueCase", "text": "obliqueCase"},
                    {"id": "partitiveCase", "text": "partitiveCase"},
                    {"id": "prolativeCase", "text": "prolativeCase"},
                    {"id": "sociativeCase", "text": "sociativeCase"},
                    {"id": "sublativeCase", "text": "sublativeCase"},
                    {"id": "superessiveCase", "text": "superessiveCase"},
                    {"id": "terminativeCase", "text": "terminativeCase"},
                    {"id": "translativeCase", "text": "translativeCase"},
                    {"id": "vocativeCase", "text": "vocativeCase"},
                    {"id": "directCase", "text": "directCase"}
                  ]
                },
                {
                  "text": "Aspect",
                  "children": 
                  [
                    {"id": "cessative", "text": "cessative"},
                    {"id": "imperfective", "text": "imperfective"},
                    {"id": "inchoative", "text": "inchoative"},
                    {"id": "perfective", "text": "perfective"},
                    {"id": "unaccomplished", "text": "unaccomplished"}
                  ]
                },
                {
                  "text": "TemporalQualifier",
                  "children": 
                  [
                    {"id": "archaicForm", "text": "archaicForm"},
                    {"id": "obsoleteForm", "text": "obsoleteForm"},
                    {"id": "outdatedForm", "text": "outdatedForm"}
                  ]
                }
  ]
var posCategories = 
  [
    {"id": "Conjunction", "text": "Conjunction"},
    {"id": "Particle", "text": "Particle"},
    {"id": "Noun", "text": "Noun"},
    {"id": "Adjective", "text": "Adjective"},
    {"id": "Article", "text": "Article"},
    {"id": "Adverb", "text": "Adverb"},
    {"id": "FusedPreposition", "text": "FusedPreposition"},
    {"id": "Pronoun", "text": "Pronoun"},
    {"id": "Adposition", "text": "Adposition"},
    {"id": "Determiner", "text": "Determiner"},
    {"id": "Symbol", "text": "Symbol"},
    {"id": "Numeral", "text": "Numeral"},
    {"id": "Verb", "text": "Verb"}
  ];
      
// add new custom element
var sentenceField = 0;

$("#addSentenceField").click(function(){
  document.getElementById("addSentenceField").disabled = true;
  sentenceField++;

  // console.log(sentenceField);
  
  
  var drow = '<form id="sentenceForm' + sentenceField +'" action="/enternewsentences" method="POST" enctype="multipart/form-data">';
  drow += '<div class="container containerremovesentencefield' + sentenceField + '"><div class="row removesentencefield' + sentenceField + '">';

  // var dItems = '<div class="col-md-6"><div class="form-group">'+
  //             '<input type="text" class="form-control"'+
  //             ' name="sentenceField' + sentenceField + '" placeholder="sentence"></div></div>';

  var sentenceAudio = '<div class="col-md-12"><div class="form-group">'+
                      '<label for="sentenceFieldAudio' + sentenceField +'">Sentence Audio</label>'+
                      '<input type="file" class="form-control" id="sentenceFieldAudio' + sentenceField +'" name="sentenceFieldAudio' + sentenceField +'">'+
                      '</div></div>';

  var dItems = '<div class="col-md-12"><div class="form-group"><div class="input-group">'+
              // '<label for="sentenceField' + sentenceField +'">Sentence</label>'+
              '<input type="text" class="form-control" name="sentenceField' + sentenceField +'"'+
              'placeholder="e.g. I have rewritten the papers" id="sentenceField' + sentenceField +'">'+
              '<div class="input-group-btn">'+
              '<button class="btn btn-danger" type="button" onclick="removeSentenceFields('+ sentenceField +');">'+
              '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div>'+
              '</div></div></div>';

    dItems += '<p><strong>Sentence with Morphemic Break</p></strong>'+
              '<p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>'+
              '<div class="col-md-12"><div class="form-group"><div class="input-group">'+
              '<input type="text" class="form-control" name="sentenceMorphemicBreak' + sentenceField +'"'+
              'placeholder="e.g. I have re-#write#-en the paper#-s"'+
              'id="sentenceMorphemicBreak' + sentenceField +'">'+
              '<div class="input-group-btn">'+
              '<button class="btn btn-success" type="button" id="checkSentenceField' + sentenceField +'" onclick="getSentence('+ sentenceField +');">'+
              '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+ 
              '</button></div>'+
              '</div></div></div>'

  drow += sentenceAudio;
  drow += dItems;
  drow += '</div></div>';
  
  drow += '</br><input class="btn btn-primary addSentences" id="submitSentenceField' + sentenceField +'" type="submit" value="Save Sentence" ></form>';
  $(".sentencefield").append(drow);
});

// remove a sentence element
function removeSentenceFields(rid) {
  $(".containerremovesentencefield"+rid).remove();
  $("#sentenceForm"+rid).remove();
  document.getElementById("addSentenceField").disabled = false;
  
}  

// var morphemePOS;

function getWordPos(morphemicSplitSentence, sid) {
  console.log('getWordPos');

  $.getJSON('/predictPOSNaiveBayes', {
    
        a:String(morphemicSplitSentence)
  }, function(data) {
        // morphemePOS = data.predictedPOS;
        morphemeFields(morphemicSplitSentence, sid, data.predictedPOS);
          // console.log(data.predictedPOS);
  });
    return false; 
}



// get the sentence enter by the user when green check button is clicked and 
// create the boxes for words and morphemes
function getSentence(sid) {
  
  document.getElementById("checkSentenceField" + sid).disabled = true; 
  console.log(sid);
  var morphemicSplitSentence = [];

  // sentence = document.getElementById("sentenceField" + sentenceField).value.trim(); // Find the text
  // sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak" + sentenceField).value.trim().replace(/#|-/g,''); // Find the text

  // console.log(sentence.localeCompare(sentence_morphemic_break))
  

  sentence = document.getElementById("sentenceField" + sentenceField).value.trim().split(' '); // Find the text
  sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak" + sentenceField).value.trim().split(' '); // Find the text
  
  
  // console.log(sentence, sentence_morphemic_break)

  if (sentence.length === 1 && sentence[0] === "") {
    alert('No input given!');
    document.getElementById("checkSentenceField" + sid).disabled = false;
    return false;
  }
  if (sentence_morphemic_break.length === 1 && sentence_morphemic_break[0] === "") {
    alert('No input given!');
    document.getElementById("checkSentenceField" + sid).disabled = false;
    return false;
  }

  for (i = 0; i < sentence_morphemic_break.length; i++) {
    if (sentence_morphemic_break[i].includes('#')) {
      morphSplit = sentence_morphemic_break[i].split('#')
      for (j = 0; j < morphSplit.length; j++) {
        morphemicSplitSentence.push(morphSplit[j]);
      }  
    }
    else {
      morphemicSplitSentence.push(sentence_morphemic_break[i]);
    }
  }
  
//   morphemePOS = getWordPos(morphemicSplitSentence)
//   setTimeout(function(){
//     console.log(morphemePOS);
// }, 1000);
  
  // console.log(sentence);
  
  console.log(morphemicSplitSentence);
  getWordPos(morphemicSplitSentence, sid)
}  

function morphemeFields(morphemicSplitSentence, sid, morphemePOS) {

  console.log(morphemePOS);
  var morphemeinput = '</br><div class="morphemefield' + sid + '">';
  morphemeinput += '<div class="row">'+
                    '<div class="col-sm-3"><strong>Morphemes</strong></div>'+
                    '<div class="col-sm-3"><strong>Gloss</strong></div>'+
                    '<div class="col-sm-3"><strong>Morph Type</strong></div>'+
                    '<div class="col-sm-3"><strong>POS</strong></div>'+
                    '</div>';
  // var morphemeinput = '';
  for(let i = 0; i < morphemicSplitSentence.length; i++) {
    // console.log(morphemePOS[i]);
    // console.log(sentence[i]);
    if (morphemicSplitSentence[i].includes('-')) {
      morphemeinput += '<div class="input-group">'+
                        '<input type="text" class="form-control" name="morphemeField' +sid+ (i+1) +'"'+'placeholder="'+morphemicSplitSentence[i]+'" value="'+morphemicSplitSentence[i]+'" id="morphemeField' +sid+ (i+1) +'"/>'+
                        '<span class="input-group-btn" style="width:50px;"></span>'+
                        '<select class="morphemicgloss' +sid+ (i+1) +'" name="morphemicgloss' +sid+ (i+1) +'" multiple="multiple" style="width: 210px"></select>'+
                        '<span class="input-group-btn" style="width:50px;"></span>'+
                        '<select class="lextype' +sid+ (i+1) +'" name="lextype' +sid+ (i+1) +'" style="width: 210px">'+
                        '<option value="affix" selected>affix</option></select>'+
                        '<span class="input-group-btn" style="width:50px;"></span></div><br>';
      // console.log(morphemeinput);                  
    }
    else {
      morphemeinput += '<div class="input-group">'+
                      '<input type="text" class="form-control" name="morphemeField' +sid+ (i+1) +'"'+'placeholder="'+morphemicSplitSentence[i]+'" value="'+morphemicSplitSentence[i]+'" id="morphemeField' +sid+ (i+1) +'"/>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<input type="text" class="form-control" name="morphemicgloss' +sid+ (i+1) +'"'+' id="morphemicgloss' +sid+ (i+1) +'"/>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<select class="lextype' +sid+ (i+1) +'" name="lextype' +sid+ (i+1) +'" style="width: 210px"></select>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<select class="pos' +sid+ (i+1) +'" name="pos' +sid+ (i+1) +'" style="width: 210px">'+
                      '<option value="'+morphemePOS[i][1]+'" selected>'+morphemePOS[i][1]+'</option>'+
                      '</select></div><br>';

    }
  }

  // add the input elements below that sentence
  $(".containerremovesentencefield"+sid).append(morphemeinput);

  var sentenceTraslationField = '<p><strong>Translation of the Sentence</strong></p><div class="col-md-12">'+
                                '<input type="text" class="form-control" name="sentenceTranslation' + sid +'"'+
                                'placeholder="Translation of the Sentence"'+
                                'id="sentenceTranslation' + sid +'">'+
                                '</div>';

  $(".containerremovesentencefield"+sid).append(sentenceTraslationField);

  for(let i = 0; i < morphemicSplitSentence.length; i++) {
    $('.morphemicgloss'+sid+(i+1)).select2({
      tags: true,
      placeholder: 'Gloss',
      data: morphemicGloss,
      allowClear: true
      // sorter: false
    });

    $('.lextype'+sid+(i+1)).select2({
      tags: true,
      placeholder: 'Morph Type',
      data: morphType
      // allowClear: true,
      // sorter: false
    });

    $('.pos'+sid+(i+1)).select2({
      tags: true,
      placeholder: 'POS',
      data: posCategories
      // allowClear: true,
      // sorter: false
      // width: 'element'
    });
    
  }
}

function editSentenceBtn() {

  console.log("Edit Sentence Button Clicked")
  
}