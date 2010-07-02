#markdown $1 | sed -e :a -e '$!N;s/^\n//;ta'
markdown $1 | sed -e '/^$/d' | sed -e :a -e '$!N;s#>\n<#><#;ta'
