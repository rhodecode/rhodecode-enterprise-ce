var _EMPTY_EXT = {'exts': [], 'mode': 'plain'};

MIME_TO_EXT = {
"application/json": {"exts": ["*.json","*.map"], "mode": "javascript"},
"application/postscript": {"exts": ["*.ps","*.eps"], "mode": ""},
"application/sieve": {"exts": ["*.siv","*.sieve"], "mode": "sieve"},
"application/typescript": {"exts": ["*.ts"], "mode": "javascript"},
"application/x-actionscript": {"exts": ["*.as"], "mode": ""},
"application/x-actionscript3": {"exts": ["*.as"], "mode": ""},
"application/x-aspx": {"exts": ["*.aspx"], "mode": "htmlembedded"},
"application/x-awk": {"exts": ["*.awk"], "mode": ""},
"application/x-befunge": {"exts": ["*.befunge"], "mode": ""},
"application/x-brainfuck": {"exts": ["*.bf","*.b"], "mode": ""},
"application/x-cheetah": {"exts": ["*.tmpl","*.spt"], "mode": ""},
"application/x-coldfusion": {"exts": ["*.cfm","*.cfml","*.cfc"], "mode": ""},
"application/x-csh": {"exts": ["*.tcsh","*.csh"], "mode": ""},
"application/x-dos-batch": {"exts": ["*.bat","*.cmd"], "mode": ""},
"application/x-ecl": {"exts": ["*.ecl"], "mode": ""},
"application/x-ejs": {"exts": ["*.ejs"], "mode": "htmlembedded"},
"application/x-evoque": {"exts": ["*.evoque"], "mode": ""},
"application/x-fantom": {"exts": ["*.fan"], "mode": ""},
"application/x-genshi": {"exts": ["*.kid"], "mode": ""},
"application/x-gettext": {"exts": ["*.pot","*.po"], "mode": ""},
"application/x-json": {"exts": ["*.json"], "mode": ""},
"application/x-jsp": {"exts": ["*.jsp"], "mode": "htmlembedded"},
"application/x-mako": {"exts": ["*.mako"], "mode": ""},
"application/x-mason": {"exts": ["*.m","*.mhtml","*.mc","*.mi","autohandler","dhandler"], "mode": ""},
"application/x-myghty": {"exts": ["*.myt","autodelegate"], "mode": ""},
"application/x-php": {"exts": ["*.phtml"], "mode": ""},
"application/x-pypylog": {"exts": ["*.pypylog"], "mode": ""},
"application/x-qml": {"exts": ["*.qml"], "mode": ""},
"application/x-sh-session": {"exts": ["*.shell-session"], "mode": ""},
"application/x-shell-session": {"exts": ["*.sh-session"], "mode": ""},
"application/x-smarty": {"exts": ["*.tpl"], "mode": ""},
"application/x-sparql-query": {"exts": [], "mode": "sparql"},
"application/x-ssp": {"exts": ["*.ssp"], "mode": ""},
"application/x-troff": {"exts": ["*.[1234567]","*.man"], "mode": ""},
"application/x-urbiscript": {"exts": ["*.u"], "mode": ""},
"application/xml": {"exts": ["*.xml","*.xsl","*.rss","*.xslt","*.xsd","*.wsdl"], "mode": "xml"},
"application/xml+evoque": {"exts": ["*.xml"], "mode": ""},
"application/xml-dtd": {"exts": ["*.dtd"], "mode": "dtd"},
"application/xquery": {"exts": ["*.xqy","*.xquery","*.xq","*.xql","*.xqm","*.xy"], "mode": "xquery"},
"application/xsl+xml": {"exts": ["*.xsl","*.xslt","*.xpl"], "mode": ""},
"jinja2": {"exts": [".jinja2"], "mode": "jinja2"},
"message/http": {"exts": [], "mode": "http"},
"text/S-plus": {"exts": ["*.S","*.R",".Rhistory",".Rprofile"], "mode": ""},
"text/apl": {"exts": ["*.dyalog","*.pgp","*.apl"], "mode": "apl"},
"text/coffeescript": {"exts": ["*.coffee"], "mode": ""},
"text/css": {"exts": ["*.css"], "mode": "css"},
"text/haxe": {"exts": ["*.hx"], "mode": ""},
"text/html": {"exts": ["*.html","*.htm","*.xhtml","*.xslt"], "mode": "htmlmixed"},
"text/html+evoque": {"exts": ["*.html"], "mode": ""},
"text/html+ruby": {"exts": ["*.rhtml"], "mode": ""},
"text/idl": {"exts": ["*.pro"], "mode": ""},
"text/javascript": {"exts": ["*.js"], "mode": "javascript"},
"text/livescript": {"exts": ["*.ls"], "mode": ""},
"text/matlab": {"exts": ["*.m"], "mode": ""},
"text/mirc": {"exts": [], "mode": "mirc"},
"text/n-triples": {"exts": ["*.nt"], "mode": "ntriples"},
"text/octave": {"exts": ["*.m"], "mode": ""},
"text/plain": {"exts": ["*.txt","*.text","*.conf","*.def","*.list","*.log"], "mode": "null"},
"text/scilab": {"exts": ["*.sci","*.sce","*.tst"], "mode": ""},
"text/smali": {"exts": ["*.smali"], "mode": ""},
"text/tiki": {"exts": [], "mode": "tiki"},
"text/vbscript": {"exts": ["*.vb","*.vbs"], "mode": "vbscript"},
"text/velocity": {"exts": ["*.vtl"], "mode": "velocity"},
"text/x-abap": {"exts": ["*.abap"], "mode": ""},
"text/x-ada": {"exts": ["*.adb","*.ads","*.ada"], "mode": ""},
"text/x-apacheconf": {"exts": [".htaccess","apache.conf","apache2.conf"], "mode": ""},
"text/x-aspectj": {"exts": ["*.aj"], "mode": ""},
"text/x-asterisk": {"exts": [], "mode": "asterisk"},
"text/x-asymptote": {"exts": ["*.asy"], "mode": ""},
"text/x-autohotkey": {"exts": ["*.ahk","*.ahkl"], "mode": ""},
"text/x-autoit": {"exts": ["*.au3"], "mode": ""},
"text/x-bmx": {"exts": ["*.bmx"], "mode": ""},
"text/x-boo": {"exts": ["*.boo"], "mode": ""},
"text/x-c": {"exts": ["*.c"], "mode": "clike"},
"text/x-c++hdr": {"exts": ["*.cpp","*.hpp","*.c++","*.h++","*.cc","*.hh","*.cxx","*.hxx","*.C","*.H","*.cp","*.CPP"], "mode": "clike"},
"text/x-c++src": {"exts": ["*.cpp","*.c++","*.cc","*.cxx","*.hpp","*.h++","*.hh","*.hxx"], "mode": "clike"},
"text/x-c-objdump": {"exts": ["*.c-objdump"], "mode": ""},
"text/x-ceylon": {"exts": ["*.ceylon"], "mode": ""},
"text/x-chdr": {"exts": ["*.c","*.h","*.idc"], "mode": "clike"},
"text/x-clojure": {"exts": ["*.clj"], "mode": "clojure"},
"text/x-cmake": {"exts": ["*.cmake","CMakeLists.txt","*.cmake.in"], "mode": "cmake"},
"text/x-cobol": {"exts": ["*.cob","*.COB","*.cpy","*.CPY"], "mode": "cobol"},
"text/x-coffeescript": {"exts": ["*.coffee"], "mode": "coffeescript"},
"text/x-common-lisp": {"exts": ["*.cl","*.lisp","*.el"], "mode": "commonlisp"},
"text/x-coq": {"exts": ["*.v"], "mode": ""},
"text/x-cpp-objdump": {"exts": ["*.cpp-objdump","*.c++-objdump","*.cxx-objdump"], "mode": ""},
"text/x-crocsrc": {"exts": ["*.croc"], "mode": ""},
"text/x-csharp": {"exts": ["*.cs"], "mode": "clike"},
"text/x-csrc": {"exts": ["*.c","*.h"], "mode": "clike"},
"text/x-cuda": {"exts": ["*.cu","*.cuh"], "mode": ""},
"text/x-cython": {"exts": ["*.pyx","*.pxd","*.pxi"], "mode": "python"},
"text/x-d": {"exts": ["*.d"], "mode": "d"},
"text/x-d-objdump": {"exts": ["*.d-objdump"], "mode": ""},
"text/x-dart": {"exts": ["*.dart"], "mode": ""},
"text/x-dg": {"exts": ["*.dg"], "mode": ""},
"text/x-diff": {"exts": ["*.diff","*.patch"], "mode": "diff"},
"text/x-dsrc": {"exts": ["*.d","*.di"], "mode": ""},
"text/x-duel": {"exts": ["*.duel","*.jbst"], "mode": ""},
"text/x-dylan": {"exts": ["*.dylan","*.dyl","*.intr"], "mode": "dylan"},
"text/x-dylan-console": {"exts": ["*.dylan-console"], "mode": ""},
"text/x-dylan-lid": {"exts": ["*.lid","*.hdp"], "mode": ""},
"text/x-echdr": {"exts": ["*.ec","*.eh"], "mode": ""},
"text/x-ecl": {"exts": ["*.ecl"], "mode": "ecl"},
"text/x-elixir": {"exts": ["*.ex","*.exs"], "mode": ""},
"text/x-erl-shellsession": {"exts": ["*.erl-sh"], "mode": ""},
"text/x-erlang": {"exts": ["*.erl","*.hrl","*.es","*.escript"], "mode": "erlang"},
"text/x-factor": {"exts": ["*.factor"], "mode": "factor"},
"text/x-fancysrc": {"exts": ["*.fy","*.fancypack"], "mode": ""},
"text/x-felix": {"exts": ["*.flx","*.flxh"], "mode": ""},
"text/x-fortran": {"exts": ["*.f","*.f90","*.F","*.F90","*.for","*.f77"], "mode": "fortran"},
"text/x-fsharp": {"exts": ["*.fs","*.fsi"], "mode": "mllike"},
"text/x-gas": {"exts": ["*.s","*.S"], "mode": "gas"},
"text/x-gfm": {"exts": ["*.md","*.MD"], "mode": "gfm"},
"text/x-gherkin": {"exts": ["*.feature"], "mode": ""},
"text/x-glslsrc": {"exts": ["*.vert","*.frag","*.geo"], "mode": ""},
"text/x-gnuplot": {"exts": ["*.plot","*.plt"], "mode": ""},
"text/x-go": {"exts": ["*.go"], "mode": "go"},
"text/x-gooddata-cl": {"exts": ["*.gdc"], "mode": ""},
"text/x-gooddata-maql": {"exts": ["*.maql"], "mode": ""},
"text/x-gosrc": {"exts": ["*.go"], "mode": ""},
"text/x-gosu": {"exts": ["*.gs","*.gsx","*.gsp","*.vark"], "mode": ""},
"text/x-gosu-template": {"exts": ["*.gst"], "mode": ""},
"text/x-groovy": {"exts": ["*.groovy"], "mode": "groovy"},
"text/x-haml": {"exts": ["*.haml"], "mode": "haml"},
"text/x-haskell": {"exts": ["*.hs"], "mode": "haskell"},
"text/x-haxe": {"exts": ["*.hx"], "mode": "haxe"},
"text/x-hybris": {"exts": ["*.hy","*.hyb"], "mode": ""},
"text/x-ini": {"exts": ["*.ini","*.cfg"], "mode": ""},
"text/x-iokesrc": {"exts": ["*.ik"], "mode": ""},
"text/x-iosrc": {"exts": ["*.io"], "mode": ""},
"text/x-irclog": {"exts": ["*.weechatlog"], "mode": ""},
"text/x-jade": {"exts": ["*.jade"], "mode": "jade"},
"text/x-java": {"exts": ["*.java"], "mode": "clike"},
"text/x-julia": {"exts": ["*.jl"], "mode": "julia"},
"text/x-kconfig": {"exts": ["Kconfig","*Config.in*","external.in*","standard-modules.in"], "mode": ""},
"text/x-koka": {"exts": ["*.kk","*.kki"], "mode": ""},
"text/x-kotlin": {"exts": ["*.kt"], "mode": "clike"},
"text/x-lasso": {"exts": ["*.lasso","*.lasso[89]"], "mode": ""},
"text/x-latex": {"exts": ["*.ltx","*.text"], "mode": "stex"},
"text/x-less": {"exts": ["*.less"], "mode": "css"},
"text/x-literate-haskell": {"exts": ["*.lhs"], "mode": "haskell-literate"},
"text/x-livescript": {"exts": ["*.ls"], "mode": "livescript"},
"text/x-llvm": {"exts": ["*.ll"], "mode": ""},
"text/x-logos": {"exts": ["*.x","*.xi","*.xm","*.xmi"], "mode": ""},
"text/x-logtalk": {"exts": ["*.lgt"], "mode": ""},
"text/x-lua": {"exts": ["*.lua","*.wlua"], "mode": "lua"},
"text/x-makefile": {"exts": ["*.mak","Makefile","makefile","Makefile.*","GNUmakefile"], "mode": ""},
"text/x-mariadb": {"exts": ["*.sql"], "mode": "sql"},
"text/x-markdown": {"exts": ["*.md","*.markdown","*.mdown","*.mkd"], "mode": "gfm"},
"text/x-minidsrc": {"exts": ["*.md"], "mode": "gfm"},
"text/x-modelica": {"exts": ["*.mo"], "mode": "modelica"},
"text/x-modula2": {"exts": ["*.def","*.mod"], "mode": ""},
"text/x-monkey": {"exts": ["*.monkey"], "mode": ""},
"text/x-moocode": {"exts": ["*.moo"], "mode": ""},
"text/x-moonscript": {"exts": ["*.moon"], "mode": ""},
"text/x-nasm": {"exts": ["*.asm","*.ASM"], "mode": ""},
"text/x-nemerle": {"exts": ["*.n"], "mode": ""},
"text/x-newlisp": {"exts": ["*.lsp","*.nl"], "mode": ""},
"text/x-newspeak": {"exts": ["*.ns2"], "mode": ""},
"text/x-nginx-conf": {"exts": ["*.conf"], "mode": "nginx"},
"text/x-nimrod": {"exts": ["*.nim","*.nimrod"], "mode": ""},
"text/x-nsis": {"exts": ["*.nsi","*.nsh"], "mode": "nsis"},
"text/x-objdump": {"exts": ["*.objdump"], "mode": ""},
"text/x-objective-c": {"exts": ["*.m","*.h"], "mode": ""},
"text/x-objective-c++": {"exts": ["*.mm","*.hh"], "mode": ""},
"text/x-objective-j": {"exts": ["*.j"], "mode": ""},
"text/x-ocaml": {"exts": ["*.ml","*.mli","*.mll","*.mly"], "mode": "mllike"},
"text/x-ooc": {"exts": ["*.ooc"], "mode": ""},
"text/x-opa": {"exts": ["*.opa"], "mode": ""},
"text/x-openedge": {"exts": ["*.p","*.cls"], "mode": ""},
"text/x-pascal": {"exts": ["*.pas","*.p"], "mode": "pascal"},
"text/x-perl": {"exts": ["*.pl","*.pm"], "mode": "perl"},
"text/x-php": {"exts": ["*.php","*.php[345]","*.inc"], "mode": "php"},
"text/x-pig": {"exts": ["*.pig"], "mode": "pig"},
"text/x-povray": {"exts": ["*.pov","*.inc"], "mode": ""},
"text/x-powershell": {"exts": ["*.ps1"], "mode": ""},
"text/x-prolog": {"exts": ["*.prolog","*.pro","*.pl"], "mode": ""},
"text/x-properties": {"exts": ["*.properties","*.ini","*.in"], "mode": "properties"},
"text/x-python": {"exts": ["*.py","*.pyw","*.sc","SConstruct","SConscript","*.tac","*.sage"], "mode": "python"},
"text/x-python-traceback": {"exts": ["*.pytb"], "mode": ""},
"text/x-python3-traceback": {"exts": ["*.py3tb"], "mode": ""},
"text/x-r-doc": {"exts": ["*.Rd"], "mode": ""},
"text/x-racket": {"exts": ["*.rkt","*.rktl"], "mode": ""},
"text/x-rebol": {"exts": ["*.r","*.r3"], "mode": ""},
"text/x-robotframework": {"exts": ["*.txt","*.robot"], "mode": ""},
"text/x-rpm-spec": {"exts": ["*.spec"], "mode": "rpm"},
"text/x-rsrc": {"exts": ["*.r"], "mode": "r"},
"text/x-rst": {"exts": ["*.rst","*.rest"], "mode": "rst"},
"text/x-ruby": {"exts": ["*.rb","*.rbw","Rakefile","*.rake","*.gemspec","*.rbx","*.duby"], "mode": "ruby"},
"text/x-rustsrc": {"exts": ["*.rs","*.rc"], "mode": "rust"},
"text/x-sass": {"exts": ["*.sass"], "mode": "sass"},
"text/x-scala": {"exts": ["*.scala"], "mode": "clike"},
"text/x-scaml": {"exts": ["*.scaml"], "mode": ""},
"text/x-scheme": {"exts": ["*.scm","*.ss"], "mode": "scheme"},
"text/x-scss": {"exts": ["*.scss"], "mode": "css"},
"text/x-sh": {"exts": ["*.sh","*.ksh","*.bash","*.ebuild","*.eclass",".bashrc","bashrc",".bash_*","bash_*"], "mode": "shell"},
"text/x-smalltalk": {"exts": ["*.st"], "mode": ""},
"text/x-smarty": {"exts": ["*.tpl"], "mode": "smarty"},
"text/x-snobol": {"exts": ["*.snobol"], "mode": ""},
"text/x-sourcepawn": {"exts": ["*.sp"], "mode": ""},
"text/x-sql": {"exts": ["*.sql"], "mode": "sql"},
"text/x-sqlite3-console": {"exts": ["*.sqlite3-console"], "mode": ""},
"text/x-squidconf": {"exts": ["squid.conf"], "mode": ""},
"text/x-standardml": {"exts": ["*.sml","*.sig","*.fun"], "mode": ""},
"text/x-stex": {"exts": [], "mode": "stex"},
"text/x-stsrc": {"exts": ["*.rs","*.rc","*.st"], "mode": "smalltalk"},
"text/x-systemverilog": {"exts": ["*.sv","*.svh","*.v"], "mode": "verilog"},
"text/x-tcl": {"exts": ["*.tcl"], "mode": "tcl"},
"text/x-tea": {"exts": ["*.tea"], "mode": ""},
"text/x-tex": {"exts": ["*.tex","*.aux","*.toc"], "mode": ""},
"text/x-tiddlywiki": {"exts": [], "mode": "tiddlywiki"},
"text/x-typescript": {"exts": ["*.ts"], "mode": ""},
"text/x-vala": {"exts": ["*.vala","*.vapi"], "mode": ""},
"text/x-vb": {"exts": ["*.vb"], "mode": "vb"},
"text/x-vbnet": {"exts": ["*.vb","*.bas"], "mode": ""},
"text/x-verilog": {"exts": ["*.v"], "mode": "verilog"},
"text/x-vhdl": {"exts": ["*.vhdl","*.vhd"], "mode": "vhdl"},
"text/x-vim": {"exts": ["*.vim",".vimrc",".exrc",".gvimrc","_vimrc","_exrc","_gvimrc","vimrc","gvimrc"], "mode": ""},
"text/x-windows-registry": {"exts": ["*.reg"], "mode": ""},
"text/x-xtend": {"exts": ["*.xtend"], "mode": ""},
"text/x-yaml": {"exts": ["*.yaml","*.yml"], "mode": "yaml"},
"text/x-z80": {"exts": ["*.z80"], "mode": "z80"},
"text/xml": {"exts": ["*.xml","*.xsl","*.rss","*.xslt","*.xsd","*.wsdl"], "mode": ""},
"text/xquery": {"exts": ["*.xqy","*.xquery","*.xq","*.xql","*.xqm"], "mode": ""}
};

/* Special case for overriding mode by file extensions
* key is extensions, value is codemirror mode
* */
_SPECIAL_CASES = {
    "md": "markdown",
    "markdown": "markdown"
};

/**
 * Get's proposed extension based on given mimetype
 *
 * @param mimetype
 * @returns extensions (default .txt)
 */
var getExtFromMimeType = function(mimetype){

    var proposed_exts = MIME_TO_EXT[mimetype] || _EMPTY_EXT;
    if(proposed_exts.exts.length < 1){
        //fallback to text/plain
        proposed_exts = {'exts': ['*.txt'], 'mode': '' }
    }
    // get the first
    var ext = proposed_exts.exts[0];
    if(ext[0] == '*'){
        ext = ext.substr(1)
    }

    return ext
};

var getMimeTypeFromExt = function(ext, multiple){
    mimetypes = [];
    for (k in MIME_TO_EXT){
        var mode = MIME_TO_EXT[k];
        if ($.inArray("*."+ext, mode.exts) != -1){
            mimetypes.push(k)
        }
    }
    if(multiple){
        return mimetypes
    }
    if(mimetypes.length > 0){
        return mimetypes[0]
    }

};

var getFilenameAndExt = function(filename){
    var parts = filename.split('.');
    var ext = null;
    var filename = null;

    if (parts.length > 1){
        var ext = parts.pop();
        var filename = parts.join("");
    }
    return {"filename": filename, "ext": ext}
}

/**
 * Detect mode from extension, this is mostly used to override the
 * detection by mimetype
 *
 * @param filename
 */
var detectCodeMirrorModeFromExt = function(filename, fallback){
    var ext = filename.split('.');
    if (ext){
        var ext = ext[ext.length-1];
    }
    // try to do a lookup by extension
    var _special_mode = _SPECIAL_CASES[ext];
    if (_special_mode){
        return _special_mode
    }
    if(fallback !== undefined && fallback === true){
        var mimetype = getMimeTypeFromExt(ext);
        if(mimetype){
            return MIME_TO_EXT[mimetype].mode;
        }

    }
}


/**
 * Try to detect a codemirror mode based on a filename and mimetype
 *
 * @param filename
 * @param mimetype
 * @returns mode or undefined
 */
var detectCodeMirrorMode = function(filename, mimetype, fallback){
    // just use _SPECIAL_CASES for detection here, as we usually got mimetype
    // and it's faster to lookup by mimetype.
    var do_fallback = fallback || false;
    var _mode_from_ext = detectCodeMirrorModeFromExt(filename, do_fallback);
    if(_mode_from_ext){
        return _mode_from_ext
    }

    // first try to match by exact mimetype
    var mode = MIME_TO_EXT[mimetype];
    if(mode && mode.mode){
        return mode.mode;
    }
}
