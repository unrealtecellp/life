var morphemicBreakSymbols = ['-', '=', '~', '<', '>', '#'];

// '-' must be the last character in the following pattern; other characters, if needed, must be added before that
var morphemicBreakRegex = /([=<>~#-])/;
var morphemicBreakReplacerRegex = /[=<>~#-]/g;
var wordBoundary = '#';
var tokenMorphIdSep = '_';