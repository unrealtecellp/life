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


// var activeSentenceMorphemicBreak = '<input type="checkbox" id="activeSentenceMorphemicBreak" name="activeSentenceMorphemicBreak" value="false">'+
//                                   '<label for="activeSentenceMorphemicBreak">&nbsp; Add Interlinear Gloss</label><br></br>'
// $(".sentencefield").append(activeSentenceMorphemicBreak);

var activeTranslationField = '<input type="checkbox" id="activeTranslationField" name="activeTranslationField" value="false">'+
                            '<label for="activeTranslationField">&nbsp; Add Translation</label><br></br>'+
                            '<div id="translationlangs" style="display: none;"></div>';
// $(".translationfield1").append(activeTranslationField);

var activeTagsField = '<input type="checkbox" id="activeTagsField" name="activeTagsField" value="false">'+
                      '<label for="activeTagsField">&nbsp; Add Tags</label><br></br>'+
                      '<div id="tags" style="display: none;">'+
                      '<div class="form-group">'+
                      '<label for="Tags">Tags</label>'+
                      '<input type="text" class="form-control" id="Tags" name="Tags">'+
                      '</div></div></div>'; 
$(".tagsfield").append(activeTagsField);

// add new custom element
var sentenceField = 1;

$("#activeSentenceMorphemicBreak").click(function() {
  activetranscriptionscript = displayRadioValue();
  activetranscriptionscriptvalue = document.getElementById(activetranscriptionscript).value;
  if (activetranscriptionscriptvalue === '') {
    document.getElementById("activeSentenceMorphemicBreak").checked=false;
    alert('No input given in the selected transcription script!');  
  }
  else {
    // const sentmorphemicbreak = document.getElementById('activeSentenceMorphemicBreak');
    // sentmorphemicbreak.setAttribute('name', 'activeSentenceMorphemicBreak_'+activetranscriptionscript);
    activeMorphSentenceField(activetranscriptionscriptvalue, activetranscriptionscript);
  }
});

function activeMorphSentenceField (value, name) {
  // console.log(value, name);
  var drow = '<div class="container containerremovesentencefield">';
              // '<div class="row removesentencefield' + sentenceField + '">';

  // var dItems = '<div id="morphemicDetail"><p><strong>Give Morphemic Break</strong></p><p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>'+
  // '<div class="col-md-12"><div class="form-group"><div class="input-group">'+
  // '<input type="text" class="form-control" name="sentenceMorphemicBreak' + sentenceField +'"'+
  // 'placeholder="e.g. I have re-#write#-en the paper#-s"'+
  // 'id="sentenceMorphemicBreak' + sentenceField +'" value="'+value+'">'+
  // '<div class="input-group-btn">'+
  // '<button class="btn btn-success" type="button" id="checkSentenceField' + sentenceField +'" onclick="getSentence('+ sentenceField +');">'+
  // '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+ 
  // '</button></div>'+
  // '</div></div></div></div>'

  var dItems = '<div id="morphemicDetail">'+
                '<p><strong>Give Morphemic Break</strong></p>'+
                '<p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>'+
                '<div class="col-md-12"><div class="form-group"><div class="input-group">'+
                '<input type="text" class="form-control" name="morphsentenceMorphemicBreak' + name +'"'+
                'placeholder="e.g. I have re-#write#-en the paper#-s"'+
                'id="sentenceMorphemicBreak' + name +'" value="'+value+'">'+
                '<div class="input-group-btn">'+
                '<button class="btn btn-success" type="button" id="checkSentenceField"'+
                'onclick="getSentence(\''+value+'\', \''+name+'\');">'+
                '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+ 
                '</button></div>'+
                '</div></div></div></div>';

  drow += dItems;
  if (document.getElementById("activeSentenceMorphemicBreak").checked) {
    document.getElementById("activeSentenceMorphemicBreak").value = true;
    $(".sentencefield").append(drow);
  }
  else {
    document.getElementById("activeSentenceMorphemicBreak").value = false;
    $(".containerremovesentencefield").remove();
  }
}

// $("#activeTranslationField").click(function() {
//   activeTranslationLangs();
// });

function activeTranslationLangs() {
  var x = document.getElementById("translationlangs");
  if (x.style.display === "none") {
    document.getElementById("activeTranslationField").value = true;
    x.style.display = "block";
  } else {
    document.getElementById("activeTranslationField").value = false;
    x.style.display = "none";
  }
}

// $("#activeTagsField").click(function() {
//   activeTags();
// });

function activeTags() {
    var x = document.getElementById("tags");
    if (x.style.display === "none") {
      document.getElementById("activeTagsField").value = true;
      x.style.display = "block";
    } else {
      document.getElementById("activeTagsField").value = false;
      x.style.display = "none";
    }
}

// remove a sentence element
function removeSentenceFields(rid) {
$(".containerremovesentencefield"+rid).remove();
$("#sentenceForm"+rid).remove();
document.getElementById("addSentenceField").disabled = false;

}  

// var morphemePOS;

function getWordPos(morphemicSplitSentence, name) {
  // console.log('getWordPos');

  $.getJSON('/predictPOSNaiveBayes', {

  a:String(morphemicSplitSentence)
  }, function(data) {
  // morphemePOS = data.predictedPOS;
  // console.log(data.predictedPOS);
  morphemeFields(morphemicSplitSentence, name, data.predictedPOS);
  
  });
  return false;
}



// get the sentence enter by the user when green check button is clicked and 
// create the boxes for words and morphemes
function getSentence(value, name) {
  // console.log(value, name);
  // document.getElementById("checkSentenceField").disabled = true; 
  // console.log(transcriptionkey, transcriptionvalue)
  
  // document.getElementById("sentenceField" + sentenceField).readonly = true; 
  // document.getElementById("sentenceMorphemicBreak" + sentenceField).readonly = true; 
  // document.getElementById("submitSentenceField" + sid).disabled = false;
  // console.log(sid);
  var morphemicSplitSentence = [];

  // sentence = document.getElementById("sentenceField" + sentenceField).value.trim(); // Find the text
  // sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak" + sentenceField).value.trim().replace(/#|-/g,''); // Find the text

  // console.log(sentence.localeCompare(sentence_morphemic_break))


  // sentence = document.getElementById("sentenceField" + sentenceField).value.trim().split(' '); // Find the text
  // sentence = document.getElementById("note").value.trim().split(' '); // Find the text
  // sentence_morphemic_break_full = document.getElementById("sentenceMorphemicBreak" + sentenceField).value.trim(); // Find the text
  // sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak" + sentenceField).value.trim().split(' '); // Find the text
  if (value === '') {
    value = document.getElementById("Transcription_" + name).value.trim();
  }
  sentence = value.trim().split(' ');
  sentence_morphemic_break_full = document.getElementById("sentenceMorphemicBreak_" + name).value.trim(); // Find the text
  sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak_" + name).value.trim().split(' '); // Find the text

  replaceObj = new RegExp('[#-]', 'g')

  // if (value !== sentence_morphemic_break_full.replaceall('#', '').replaceall('-', '')) {
  if (value !== sentence_morphemic_break_full.replace(replaceObj, '')) {
    alert('Sentence do not match to: '+value)
    return false;
  }
  // else {
  //   // disableEditIcon(name, value);
  //   document.getElementById("sentenceMorphemicBreak_"+name).readOnly = true;
  //   var checkBtn = '<button class="btn btn-warning" type="button" id="editSentenceField"'+
  //               'onclick="editMorphemicBreakSentence(\''+value+'\', \''+name+'\');">'+
  //               '<span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button>';
  //   $("#editsentmorpbreak").html(checkBtn);
  // }


  // console.log(sentence, sentence_morphemic_break)

  if (sentence.length === 1 && sentence[0] === "") {
  alert('No input given!');
  // document.getElementById("checkSentenceField" + sid).disabled = false;
  document.getElementById("checkSentenceField").disabled = false;
  return false;
  }
  if (sentence_morphemic_break.length === 1 && sentence_morphemic_break[0] === "") {
  alert('No input given!');
  document.getElementById("checkSentenceField").disabled = false;
  return false;
  }

  if (sentence_morphemic_break_full.includes('-')) {
    morph_len = (sentence_morphemic_break_full.match(/-/g)||[]).length;
    boundary_len = (sentence_morphemic_break_full.match(/#/g)||[]).length;

    // console.log(morph_len)
    // console.log(boundary_len)
    
    if (boundary_len > morph_len) {
      alert("Number of # ("+boundary_len+") should be less than or equal to number of - ("+morph_len+") in the morphemic break")
      // document.getElementById("checkSentenceField" + sid).disabled = false;
      document.getElementById("checkSentenceField").disabled = false;
      return false;
    }



    // alert('No input given!');
    // document.getElementById("checkSentenceField" + sid).disabled = false;
    // return false;
  }
  // sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak" + sentenceField).value.trim().split(' '); // Find the text

  for (i = 0; i < sentence_morphemic_break.length; i++) {
    if (sentence_morphemic_break[i].includes('#') || sentence_morphemic_break[i].includes('-')) {
      if (sentence_morphemic_break[i].includes('#') && sentence_morphemic_break[i].includes('-')) {
        morphSplit = sentence_morphemic_break[i].split('#')

        if (morphSplit.length <= 3) {
          for (j = 0; j < morphSplit.length; j++) {
            var currentMorph = morphSplit[j]
            if (currentMorph.includes("-")) {
              var dashIndex = currentMorph.indexOf("-")
              var morphemes = currentMorph.split("-")

              for (k = 0; k < morphemes.length; k++){
                if (morphemes[k].trim() !== "") {
                  if (dashIndex == 0) {
                    morphemicSplitSentence.push("-"+morphemes[k]);
                  }
                  else{
                    morphemicSplitSentence.push(morphemes[k]+"-");
                  }
                }
              }
            }
            else if (currentMorph.trim() !== "") {
              morphemicSplitSentence.push(currentMorph);
            }
          }
        }
        else {
          alert("Number of # should be less than or equal to 2 in <<"+ sentence_morphemic_break[i] + ">>");
          document.getElementById("checkSentenceField").disabled = false;
          return false;
        } 
      }
      else {
        if (sentence_morphemic_break[i].includes('#')) {
          alert("- is missing in the morphemic break in <<"+ sentence_morphemic_break[i] + ">>");
        }
        else {
          alert("# is missing in the morphemic break in <<"+ sentence_morphemic_break[i] + ">>");
        }
      // document.getElementById("checkSentenceField" + sid).disabled = false;
        document.getElementById("checkSentenceField").disabled = false;
        return false;
      }
    }
    else {
      morphemicSplitSentence.push(sentence_morphemic_break[i]);
    }
  }
  console.log('morphemicSplitSentence', morphemicSplitSentence)

  document.getElementById("sentenceMorphemicBreak_"+name).readOnly = true;
  var checkBtn = '<button class="btn btn-warning" type="button" id="editSentenceField"'+
              'onclick="editMorphemicBreakSentence(\''+value+'\', \''+name+'\');">'+
              '<span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button><br>';
  $("#editsentmorpbreak").html(checkBtn);

  //   morphemePOS = getWordPos(morphemicSplitSentence)
  //   setTimeout(function(){
  //     console.log(morphemePOS);
  // }, 1000);

  // console.log(sentence);

  // console.log(morphemicSplitSentence);
  getWordPos(morphemicSplitSentence, name)
}  

function morphemeFields(morphemicSplitSentence, name, morphemePOS) {

  // console.log(morphemePOS);
  var morphemeinput = '<div class="morphemefield_' + name + '">';
  morphemeinput += '<div class="row">'+
  '<div class="col-sm-3"><strong>Morphemes</strong></div>'+
  '<div class="col-sm-3"><strong>Gloss</strong></div>'+
  '<div class="col-sm-3"><strong>Morph Type</strong></div>'+
  '<div class="col-sm-3"><strong>POS</strong></div>'+
  '</div>';
  // var morphemeinput = '';
  morphemeCount = morphemicSplitSentence.length
  for(let i = 0; i < morphemeCount; i++) {
    // console.log(morphemePOS[i]);
    // console.log(sentence[i]);
    if (morphemicSplitSentence[i].includes('-')) {
    morphemeinput += '<div class="input-group">'+
        '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
        'placeholder="'+ morphemicSplitSentence[i] +'" value="'+morphemicSplitSentence[i]+'"'+
        'id="morphemeField' + name + (i+1) +'" readonly/>'+
        '<span class="input-group-btn" style="width:50px;"></span>'+
        '<select class="morphemicgloss' + name + (i+1) +'" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
        ' multiple="multiple" style="width: 210px"></select>'+
        '<span class="input-group-btn" style="width:50px;"></span>'+
        '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'" style="width: 210px">'+
        '<option value="affix" selected>affix</option></select>'+
        '<span class="input-group-btn" style="width:50px;"></span></div><br>';
    // console.log(morphemeinput);                  
    }
    else {
    morphemeinput += '<div class="input-group">'+
      '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
      'placeholder="'+ morphemicSplitSentence[i] +'" value="'+ morphemicSplitSentence[i] +'"'+
      'id="morphemeField' + name + (i+1) +'" readonly/>'+
      '<span class="input-group-btn" style="width:50px;"></span>'+
      '<input type="text" class="form-control" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
      ' id="morphemicgloss' + name + (i+1) +'"/>'+
      '<span class="input-group-btn" style="width:50px;"></span>'+
      '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'" style="width: 210px"></select>'+
      '<span class="input-group-btn" style="width:50px;"></span>'+
      '<select class="pos' + name + (i+1) +'" name="morph_pos_' + name + '_' +  (i+1) +'" style="width: 210px">'+
      '<option value="'+ morphemePOS[i][1] +'" selected>'+ morphemePOS[i][1] +'</option>'+
      '</select></div><br>';

    }
  }
  morphemeinput += ' <input type="text" id="morphcount" name="morphcount'+ name +'" value="'+ morphemeCount +'" hidden>'
  // add the input elements below that sentence
  // $(".containerremovesentencefield"+sid).append(morphemeinput);
  // $(".containerremovesentencefield").append(morphemeinput);
  // console.log(morphemeinput)
  // console.log(".morphemicDetail_"+name)
  $(".morphemefield_"+name).remove();
  $("#morphemicDetail_"+name).append(morphemeinput);



  // var sentenceTraslationField = '<input type="checkbox" id="activeSentenceMorphemicBreak" name="activeSentenceMorphemicBreak" value="false" onclick="activeTranscriptionScript()">'+
  // '<label for="activeSentenceMorphemicBreak">&nbsp; Add Translation</label><br></br>'
              // '<p><strong>Translation of the Sentence</strong></p><div class="col-md-12">'+
              // '<input type="text" class="form-control" name="sentenceTranslation' + sid +'"'+
              // 'placeholder="Translation of the Sentence"'+
              // 'id="sentenceTranslation' + sid +'">'+
              // '</div>';
  // var sentenceTraslationField = '<input type="checkbox" id="activeSentenceMorphemicBreak" name="activeSentenceMorphemicBreak" value="false" onclick="activeTranscriptionScript()">'+
  //             '<label for="activeSentenceMorphemicBreak">&nbsp; Add Translation</label><br></br>'+
  //             '<p><strong>Translation in Hindi</strong></p><div class="col-md-12">'+
  //             '<input type="text" class="form-control" name="sentenceTranslation' + sid +'"'+
  //             'placeholder="Translation of the Sentence"'+
  //             'id="sentenceTranslation' + sid +'">'+
  //             '</div>'+
  //             '<p><strong>Translation in Tamil</strong></p><div class="col-md-12">'+
  //             '<input type="text" class="form-control" name="sentenceTranslation' + sid +'"'+
  //             'placeholder="Translation of the Sentence"'+
  //             'id="sentenceTranslation' + sid +'">'+
  //             '</div>';
  // var sentenceTraslationField = '<p><strong>Translation of the Sentence</strong></p><div class="col-md-12">'+
  //             '<input type="text" class="form-control" name="sentenceTranslation' + sid +'"'+
  //             'placeholder="Translation of the Sentence"'+
  //             'id="sentenceTranslation' + sid +'">'+
  //             '</div>';

  // $(".containerremovesentencefield"+sid).append(sentenceTraslationField);

  for(let i = 0; i < morphemicSplitSentence.length; i++) {
  $('.morphemicgloss'+ name +(i+1)).select2({
  tags: true,
  placeholder: 'Gloss',
  data: morphemicGloss,
  allowClear: true
  // sorter: false
  });

  $('.lextype'+ name +(i+1)).select2({
  tags: true,
  placeholder: 'Morph Type',
  data: morphType
  // allowClear: true,
  // sorter: false
  });

  $('.pos'+ name +(i+1)).select2({
  tags: true,
  placeholder: 'POS',
  data: posCategories
  // allowClear: true,
  // sorter: false
  // width: 'element'
  });

  }
  // document.getElementById("submitSentenceField").disabled = false;
  // $('.submitSentenceField').removeAttr('disabled');
  // document.getElementById("sentenceField" + sentenceField).readOnly = true; 
  // document.getElementById("sentenceMorphemicBreak" + sentenceField).readOnly = true; 
  // document.getElementById("submitSentenceField" + sid).disabled = false;
}


function editMorphemicBreakSentence(transcriptionvalue, transcriptionkey) {
  // console.log(transcriptionkey, transcriptionvalue)
  document.getElementById("sentenceMorphemicBreak_"+transcriptionkey).readOnly = false;
  var checkBtn = '<button class="btn btn-success" type="button" id="checkSentenceField"'+
              'onclick="getSentence(\''+transcriptionvalue+'\', \''+transcriptionkey+'\');">'+
              '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span></button>';

  $("#editsentmorpbreak").html(checkBtn);
}

$("#save").click(function() {
  // console.log('sending transcription and morphemic details to the server');
  var transcriptionData = Object()
  var transcriptionRegions = localStorage.regions
  var lastActiveId = document.getElementById("lastActiveId").value;
  transcriptionData['lastActiveId'] = lastActiveId
  transcriptionData['transcriptionRegions'] = transcriptionRegions
  // console.log(transcriptionData)
  $.getJSON('/savetranscription', {
  
  a:JSON.stringify(transcriptionData)
  }, function(data) {
      window.location.reload();
  });
  return false; 
});

function myFunction(newData) {
  localStorage.setItem("activeprojectform", JSON.stringify(newData));
  // console.log(newData);
  localStorage.setItem("regions", JSON.stringify(newData['transcriptionRegions']));
  // var activeAudioFilename = JSON.parse(localStorage.getItem('AudioFilePath')).split('/')[2];
  var activeAudioFilename = newData["AudioFilePath"].split('/')[2];
  if (activeAudioFilename === undefined) {
    activeAudioFilename = '';
  }
  // console.log(activeAudioFilename)
  var inpt = '<strong>Audio Filename: </strong><strong id="audioFilename">'+ activeAudioFilename +'</strong>'
  $(".defaultfield").append(inpt);
  lastActiveId = newData["lastActiveId"]
  // console.log(lastActiveId)
  inpt = '<input type="hidden" id="lastActiveId" name="lastActiveId" value="'+lastActiveId+'">';
  $('.defaultfield').append(inpt);
  inpt = ''
  // localStorage.removeItem('regions');
  localStorage.setItem("transcriptionDetails", JSON.stringify([newData['transcriptionDetails']]));
  localStorage.setItem("AudioFilePath", JSON.stringify(newData['AudioFilePath']));
  for (let [key, value] of Object.entries(newData)){
    // console.log(key, value);
    if (key === 'Sentence Language') {
      inpt += '<div class="col"><div class="form-group">'+
                  '<label for="'+key+'">'+key+'</label>'+
                  '<input type="text" class="form-control" id="'+key+'" name="'+key+'" value="'+newData[key]+'" readonly>'+
                  '</div></div>'; 
          $('.lexemelang').append(inpt);
          inpt = '';
        }
    // else if (key === 'Transcription Script') {
    //   var transcriptionScriptLocalStorage = []
    //   var transcriptionScript = newData[key];
    //   var interLinearGlossLang = ''
    //   var interLinearGlossScript = ''
    //     for (var i = 0; i < transcriptionScript.length; i++) {
    //       if (transcriptionScript[i].includes('_')) {
    //         // console.log(transcriptionScript[i]);
    //         lScript = transcriptionScript[i].replace('_', ' ');
    //       }
    //       else {
    //         lScript = transcriptionScript[i];
    //       }
    //       inpt += '<div class="form-group">';
    //       if (i === 0) {
    //         inpt += '<input type="radio" id="TranscriptionRadioBtn'+ transcriptionScript[i] +'" name="activeTranscriptionScript"'+
    //                 'value="Transcription_'+ transcriptionScript[i] +'" checked>';
    //       }
    //       else {
    //         inpt += '<input type="radio" id="TranscriptionRadioBtn'+ transcriptionScript[i] +'" name="activeTranscriptionScript"'+
    //                 'value="Transcription_'+ transcriptionScript[i] +'">';
    //       }                
    //       inpt += '<label for="Transcription_'+ transcriptionScript[i] +'">Transcription in '+ lScript +'</label>'+
    //             '<input type="text" class="form-control" id="Transcription_'+ transcriptionScript[i] +'"'+ 
    //             'placeholder="Transcription '+ lScript +'" name="Transcription_'+ transcriptionScript[i] +'">'+
    //             '</div></div>';
    //       transcriptionScriptLocalStorage.push(transcriptionScript[i]);
    //     }
    //     $('.transcription').append(inpt);
    //     inpt = '';
    //     localStorage.setItem("Transcription Script", JSON.stringify(transcriptionScriptLocalStorage));
    // }
    // else if (key === 'Translation Language') {
    //   translationLang = newData[key];
    //     for (var i = 0; i < translationLang.length; i++) {
    //       inpt += '<div class="form-group">'+
    //               '<label for="'+ translationLang[i] +'Translation">Translation in '+ translationLang[i] +'</label>'+
    //               '<input type="text" class="form-control" id="'+ translationLang[i] +'Translation"'+ 
    //               'placeholder="Translation '+ translationLang[i] +'" name="Translation '+ translationLang[i] + '">'+
    //               '</div></div>';          
    //     }
    //   $('#translationlangs').append(inpt);
    //   inpt = '';
    // }
    // else if (key === 'Interlinear Gloss Language') {
    //   interLinearGlossLang = newData[key]
    // }
    // else if (key === 'Interlinear Gloss Script') {
    //   interLinearGlossScript = newData[key]
    // }
  }
  // interLinearGlossLangScriptMapping = mapArrays(interLinearGlossLang, interLinearGlossScript)
  // localStorage.setItem("Interlinear Gloss Lang Script", JSON.stringify(interLinearGlossLangScriptMapping));
  // for (k=0; k<=1000; k++) {
  //   console.log(Date.now())
  //   // datetime = new Date()
  //   // console.log(datetime.toJSON(), datetime.getMilliseconds());
  // }
}

function mapArrays(array_1, array_2) {
  if(array_1.length != array_2.length || 
      array_1.length == 0 || 
      array_2.length == 0) {
      return null;
     }
     let mappedData = new Object();
       
   // Using the foreach method
   array_1.forEach((k, i) => {mappedData[k] = array_2[i]})
     return mappedData;
}

function displayRadioValue() {
  var ele = document.getElementsByName('activeTranscriptionScript');
  activetranscriptionscript = ''
  for(i = 0; i < ele.length; i++) {
      if(ele[i].checked)
        activetranscriptionscript =  ele[i].value
  }
  return activetranscriptionscript
}


function previousAudio() {
  var lastActiveId = document.getElementById("lastActiveId").value;
  // console.log(lastActiveId)
    $.ajax({
        url: '/loadpreviousaudio',
        type: 'GET',
        data: {'data': JSON.stringify(lastActiveId)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
          // console.log(response.newAudioFilePath)
          // localStorage.setItem("AudioFilePath", JSON.stringify(response.newAudioFilePath));
          window.location.reload(); 
        }
    });
    return false;
}

function nextAudio() {
  // lastActiveFilename = document.getElementById("audioFilename").innerHTML;
  var lastActiveId = document.getElementById("lastActiveId").value;
  // console.log(lastActiveFilename)
    $.ajax({
        url: '/loadnextaudio',
        type: 'GET',
        data: {'data': JSON.stringify(lastActiveId)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
          // console.log(response.newAudioFilePath)
          // localStorage.setItem("AudioFilePath", JSON.stringify(response.newAudioFilePath));
          window.location.reload();
        }
    });
    return false;
}

function unAnnotated() {
  unanno = '';
  $('#uNAnnotated').remove();
  $.ajax({
      url: '/allunannotated',
      type: 'GET',
      data: {'data': JSON.stringify(unanno)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          allunanno = response.allunanno;
          allanno = response.allanno;
          // console.log(allanno)
          var inpt = '';
          inpt += '<select class="col-sm-3 allanno" id="allanno" onchange="loadAnnoText()">'+
                  '<option selected disabled>Completed</option>';
                  for (i=0; i<allanno.length; i++) {
                      inpt += '<option value="'+allanno[i]+'">'+allanno[i]+'</option>';
                  }
          inpt += '</select>';
          inpt += '<select class="pr-4 col-sm-3" id="allunanno" onchange="loadUnAnnoText()">'+
                  '<option selected disabled>Not Completed</option>';
                  for (i=0; i<allunanno.length; i++) {
                      inpt += '<option value="'+allunanno[i]+'">'+allunanno[i]+'</option>';
                  }
          inpt += '</select>';
          $('.commentIDs').append(inpt);
          // console.log(inpt);
      }
  });
  return false; 
}

function loadUnAnnoText() {
  newAudioFilename = document.getElementById('allunanno').value;
  console.log(newAudioFilename)
  // loadRandomAudio(newAudioFilename)
  $.ajax({
      url: '/loadunannotext',
      type: 'GET',
      data: {'data': JSON.stringify(newAudioFilename)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          window.location.reload();
      }
  });
  return false;
}

function loadAnnoText() {
  newAudioFilename = document.getElementById('allanno').value;
  console.log(newAudioFilename)
  // loadRandomAudio(newAudioFilename)
  $.ajax({
      url: '/loadunannotext',
      type: 'GET',
      data: {'data': JSON.stringify(newAudioFilename)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          window.location.reload();
      }
  });
  return false;
}

function loadRandomAudio(newAudioFilename) {
  filePath = JSON.parse(localStorage.getItem('AudioFilePath'));
  // console.log(typeof filePath)
  currentAudioFilename = filePath.split('/')[2];
  newfilePath = filePath.replace(currentAudioFilename, newAudioFilename)
  localStorage.setItem("AudioFilePath", JSON.stringify(newfilePath));
  window.location.reload();
}

$('#speakeridsdropdown').select2({
  // tags: true,
  placeholder: 'select speaker',
  // data: posCategories
  // allowClear: true,
  // sorter: false
  // width: 'element'
  });

$('#speakeriduploaddropdown').select2({
  // tags: true,
  placeholder: 'select speaker',
  // data: posCategories
  // allowClear: true,
  // sorter: false
  // width: 'element'
  });

$("#audiofile").change(function() {
    let zipFileElement = document.getElementById('audiofile');
    zipFileName = zipFileElement.files[0];
    console.log(zipFileName);
    // displayZipFileName = '<p>'+zipFileName.name+'</p>';
    // $("#displayZipFileName").append(zipFileName.name);
    zipFileSize = zipFileName.size
    console.log(typeof zipFileSize, Math.round((zipFileSize/1024)));
    if (! (zipFileSize <= 200000000)) {
      
      const size = (zipFileSize / 1000 / 1000).toFixed(2);
      console.log(zipFileSize, size);
      alert('Please upload file upto 200 MB. This file size is: ' + size + " MB");
      window.location.reload(true);
    }
    
})

function replaceZoomSlider() {
  // const element = document.getElementById("slider");
  // element.remove();
  // console.log('replaceZoomSlider()')
  let slider = '<input id="slider" data-action="zoom" type="range" min="20" max="100" value="0" style="width: 50%">';
  $("#sliderdivid").html(slider);
}

replaceZoomSlider();