if(typeof keyman === 'undefined') {console.log('Keyboard requires KeymanWeb 10.0 or later');if(typeof tavultesoft !== 'undefined') tavultesoft.keymanweb.util.alert("This keyboard requires KeymanWeb 10.0 or later");} else {KeymanWeb.KR(new Keyboard_itrans_gurmukhi());}function Keyboard_itrans_gurmukhi(){this.KI="Keyboard_itrans_gurmukhi";this.KN="Gurmukhi Phonetic (ITRANS)";this.KMINVER="10.0";this.KV={F:' 1em "Nirmala UI"',K102:0};this.KV.KLS={"default": ["`","੧","੨","੩","੪","੫","੬","੭","੮","੯","੦","-","=","","","","ਗ਼੍","ੵ","ਏ","ਰ੍","ਤ੍","ਯ੍","ਉ","ਇ","ਓ","ਪ੍","[","]","\\","","","","ਅ","ਸ੍","ਦ੍","ਫ਼੍","ਗ੍","ਹ੍","ਜ੍","ਕ੍","ਲ੍",";","'","","","","","","","ਜ਼੍","ਖ਼੍","ਚ੍","ਵ੍","ਬ੍","ਨ੍","ਮ੍",",",".","/","","","","","",""],"shift": ["~","!","@","ੴ","ੳ","ੲ","੍","ੵ","☬","(",")","‌","‍","","","","","","","ੜ੍","ਟ੍","ਞ੍","ਊ","ਈ","","ਫ੍","{","}","|","","","","ਆ","ਸ਼੍","ਡ੍","","ਘ੍","ਃ","ਝ੍","ਖ੍","ਲ਼੍",":","\"","","","","","","","","","ਛ੍","","ਭ੍","ਣ੍","ੰ","ਂ","ੱ","?","","","","","",""]};this.KV.BK=(function(x){var e=Array.apply(null,Array(65)).map(String.prototype.valueOf,""),r=[],v,i,m=['default','shift','ctrl','shift-ctrl','alt','shift-alt','ctrl-alt','shift-ctrl-alt'];for(i=m.length-1;i>=0;i--)if((v=x[m[i]])||r.length)r=(v?v:e).slice().concat(r);return r})(this.KV.KLS);this.KDU=1;this.KH="Uses Unshifted, Shifted layouts.";this.KM=0;this.KBVER="1.0.0";this.KMBM=0x0010;this.s7="©2019 sanskritdocuments.org";this.s14="!()-:;?{}\",.=\\|[]`'/";this.s15="0123456789";this.s16="੦੧੨੩੪੫੬੭੮੯";this.s17="ਕਖਗਘਙਚਛਜਝਞਟਠਡਢਣਤਥਦਧਨਪਫਬਭਮਯਰਲਲ਼ਵਸ਼ਸਹਖ਼ਗ਼ਜ਼ੜਫ਼";this.s18="eiouAIU";this.s19="ੇਿੋੁਾੀੂ";this.s20="aiu";this.s21="ਾੈੌ";this.s22="!()-:;?{}\",.=\\|[]`'/ ";this.s23="M<";this.s24="ਾੀੈੌ";this.KVER="11.0.1356.0";this.gs=function(t,e) {return this.g0(t,e);};this.g0=function(t,e) {var k=KeymanWeb,r=0,m=0;if(k.KKM(e,16384,8)) {if(k.KFCM(1,t,[{t:'a',a:this.s16}])){r=m=1;k.KDC(1,t);k.KIO(-1,this.s15,1,t);}}else if(k.KKM(e,16384,32)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t," ");}}else if(k.KKM(e,16400,49)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"!");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"!");}}else if(k.KKM(e,16400,222)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"\"");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"\"");}}else if(k.KKM(e,16400,51)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੴ");}}else if(k.KKM(e,16400,52)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੳ");}}else if(k.KKM(e,16400,53)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੲ");}}else if(k.KKM(e,16400,55)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੵ");}}else if(k.KKM(e,16384,222)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"'");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"'");}}else if(k.KKM(e,16400,57)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"(");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"(");}}else if(k.KKM(e,16400,48)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,")");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,")");}}else if(k.KKM(e,16400,56)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"☬");}}else if(k.KKM(e,16400,187)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"‍");}}else if(k.KKM(e,16384,188)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,",");}else if(k.KFCM(1,t,[','])){r=m=1;k.KDC(1,t);k.KO(-1,t,"੶");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,",");}}else if(k.KKM(e,16384,189)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"-");}else if(k.KFCM(1,t,['-'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"–");}else if(k.KFCM(1,t,['–'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"—");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"-");}}else if(k.KKM(e,16384,190)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,".");}else if(k.KFCM(1,t,['.'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"।");}else if(k.KFCM(1,t,['।'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"॥");}else if(k.KFCM(1,t,['॥'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"…");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,".");}}else if(k.KKM(e,16384,191)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"/");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"/");}}else if(k.KKM(e,16384,48)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੦");}}else if(k.KKM(e,16384,49)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੧");}}else if(k.KKM(e,16384,50)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੨");}}else if(k.KKM(e,16384,51)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੩");}}else if(k.KKM(e,16384,52)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੪");}}else if(k.KKM(e,16384,53)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੫");}}else if(k.KKM(e,16384,54)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੬");}}else if(k.KKM(e,16384,55)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੭");}}else if(k.KKM(e,16384,56)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੮");}}else if(k.KKM(e,16384,57)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੯");}}else if(k.KKM(e,16400,186)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,":");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,":");}}else if(k.KKM(e,16384,186)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,";");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,";");}}else if(k.KKM(e,16400,188)) {if(k.KFCM(1,t,[{t:'a',a:this.s24}])){r=m=1;k.KDC(1,t);k.KIO(-1,this.s24,1,t);k.KO(-1,t,"ਂ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਂ");}}else if(k.KKM(e,16384,187)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"=");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"=");}}else if(k.KKM(e,16400,190)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੱ");}}else if(k.KKM(e,16400,191)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"?");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"?");}}else if(k.KKM(e,16400,50)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"@");}}else if(k.KKM(e,16400,65)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ਾ");}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਾ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਆ");}}else if(k.KKM(e,16400,66)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਭ੍");}}else if(k.KKM(e,16400,67)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਛ੍");}}else if(k.KKM(e,16400,68)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਡ੍");}}else if(k.KKM(e,16400,69)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16400,70)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16400,71)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਘ੍");}}else if(k.KKM(e,16400,72)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਃ");}}else if(k.KKM(e,16400,73)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੀ");}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੀ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਈ");}}else if(k.KKM(e,16400,74)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਝ੍");}}else if(k.KKM(e,16400,75)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਖ੍");}}else if(k.KKM(e,16400,76)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਲ਼੍");}}else if(k.KKM(e,16400,77)) {if(k.KFCM(1,t,['ੰ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਁ");}else if(k.KFCM(1,t,[{t:'a',a:this.s24}])){r=m=1;k.KDC(1,t);k.KIO(-1,this.s24,1,t);k.KO(-1,t,"ਂ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੰ");}}else if(k.KKM(e,16400,78)) {if(k.KFCM(1,t,['~'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਙ੍");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਣ੍");}}else if(k.KKM(e,16400,79)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16400,80)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਫ੍");}}else if(k.KKM(e,16400,81)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16400,82)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੜ੍");}}else if(k.KKM(e,16400,83)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਸ਼੍");}}else if(k.KKM(e,16400,84)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਟ੍");}}else if(k.KKM(e,16400,85)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੂ");}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੂ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਊ");}}else if(k.KKM(e,16400,86)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16400,87)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16400,88)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16400,89)) {if(k.KFCM(2,t,['ਘ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਜ੍ਞ੍");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਞ੍");}}else if(k.KKM(e,16400,90)) {if(1){r=m=1;k.KDC(0,t);k.KB(t);}}else if(k.KKM(e,16384,219)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"[");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"[");}}else if(k.KKM(e,16384,220)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"\\");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"\\");}}else if(k.KKM(e,16384,221)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"]");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"]");}}else if(k.KKM(e,16400,54)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"੍‌");}else if(k.KFCM(1,t,[{t:'a',a:this.s17}])){r=m=1;k.KDC(1,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"੍‌");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"੍");}}else if(k.KKM(e,16400,189)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"‌");}}else if(k.KKM(e,16384,192)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"`");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"`");}}else if(k.KKM(e,16384,65)) {if(k.KFCM(2,t,['@','a'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਾ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"@a");}else if(k.KFCM(1,t,['ਅ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਆ");}else if(k.KFCM(1,t,[{t:'a',a:this.s17}])){r=m=1;k.KDC(1,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ਾ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਅ");}}else if(k.KKM(e,16384,66)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਬ੍");}}else if(k.KKM(e,16384,67)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਚ੍");}}else if(k.KKM(e,16384,68)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਦ੍");}}else if(k.KKM(e,16384,69)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੇ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'ੇ'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੀ");}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੇ");}else if(k.KFCM(1,t,['ੇ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੀ");}else if(k.KFCM(1,t,['ਏ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਈ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਏ");}}else if(k.KKM(e,16384,70)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਫ਼੍");}}else if(k.KKM(e,16384,71)) {if(k.KFCM(2,t,['ਣ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਙ੍");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਗ੍");}}else if(k.KKM(e,16384,72)) {if(k.KFCM(2,t,['ਕ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਖ੍");}else if(k.KFCM(2,t,['ਗ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਘ੍");}else if(k.KFCM(2,t,['ਚ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਚ੍");}else if(k.KFCM(2,t,['ਛ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਛ੍");}else if(k.KFCM(2,t,['ਜ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਝ੍");}else if(k.KFCM(2,t,['ਟ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਠ੍");}else if(k.KFCM(2,t,['ਡ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਢ੍");}else if(k.KFCM(2,t,['ਤ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਥ੍");}else if(k.KFCM(2,t,['ਦ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਧ੍");}else if(k.KFCM(2,t,['ਪ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਫ੍");}else if(k.KFCM(2,t,['ਬ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਭ੍");}else if(k.KFCM(2,t,['ਸ','੍'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ਸ਼੍");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਹ੍");}}else if(k.KKM(e,16384,73)) {if(k.KFCM(2,t,['@','a'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ੈ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ਿ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'ਿ'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੀ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'ੇ'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੈ");}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਿ");}else if(k.KFCM(1,t,['ਿ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੀ");}else if(k.KFCM(1,t,['ੇ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੈ");}else if(k.KFCM(1,t,['ਇ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਈ");}else if(k.KFCM(1,t,['ਅ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਐ");}else if(k.KFCM(1,t,['ਏ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਐ");}else if(k.KFCM(1,t,[{t:'a',a:this.s17}])){r=m=1;k.KDC(1,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੈ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਇ");}}else if(k.KKM(e,16384,74)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਜ੍");}}else if(k.KKM(e,16384,75)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਕ੍");}}else if(k.KKM(e,16384,76)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਲ੍");}}else if(k.KKM(e,16384,77)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਮ੍");}}else if(k.KKM(e,16384,78)) {if(k.KFCM(1,t,['~'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਞ੍");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਨ੍");}}else if(k.KKM(e,16384,79)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੋ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'ੋ'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੂ");}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੋ");}else if(k.KFCM(1,t,['ੋ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੂ");}else if(k.KFCM(1,t,['ਓ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਊ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਓ");}}else if(k.KKM(e,16384,80)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਪ੍");}}else if(k.KKM(e,16384,81)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਗ਼੍");}}else if(k.KKM(e,16384,82)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਰ੍");}}else if(k.KKM(e,16384,83)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਸ੍");}}else if(k.KKM(e,16384,84)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਤ੍");}}else if(k.KKM(e,16384,85)) {if(k.KFCM(2,t,['@','a'])){r=m=1;k.KDC(2,t);k.KO(-1,t,"ੌ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੁ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'ੁ'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੂ");}else if(k.KFCM(2,t,[{t:'a',a:this.s17},'ੋ'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੌ");}else if(k.KFCM(1,t,['@'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੁ");}else if(k.KFCM(1,t,['ੁ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੂ");}else if(k.KFCM(1,t,['ੋ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ੌ");}else if(k.KFCM(1,t,['ਉ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਊ");}else if(k.KFCM(1,t,['ਅ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਔ");}else if(k.KFCM(1,t,['ਓ'])){r=m=1;k.KDC(1,t);k.KO(-1,t,"ਔ");}else if(k.KFCM(1,t,[{t:'a',a:this.s17}])){r=m=1;k.KDC(1,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"ੌ");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਉ");}}else if(k.KKM(e,16384,86)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਵ੍");}}else if(k.KKM(e,16384,87)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ੵ");}}else if(k.KKM(e,16384,88)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਖ਼੍");}}else if(k.KKM(e,16384,89)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਯ੍");}}else if(k.KKM(e,16384,90)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"ਜ਼੍");}}else if(k.KKM(e,16400,219)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"{");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"{");}}else if(k.KKM(e,16400,220)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"|");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"|");}}else if(k.KKM(e,16400,221)) {if(k.KFCM(2,t,[{t:'a',a:this.s17},'੍'])){r=m=1;k.KDC(2,t);k.KIO(-1,this.s17,1,t);k.KO(-1,t,"}");}else if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"}");}}else if(k.KKM(e,16400,192)) {if(1){r=m=1;k.KDC(0,t);k.KO(-1,t,"~");}}return r;};}