/***************************************************************************
getopt(3C)                                                       getopt(3C)
PROGRAM FILE NAME: getopt.c
getopt - get option letter from argument vector
SYNOPSIS
     int getopt(int argc, char * const argv[], const char *optstring);
extern char *optarg;
     extern int optind, opterr, optopt;
PRORGAM DESCRIPTION:
     getopt returns the next option letter in argv (starting from argv[1])
     that matches a letter in optstring.  optstring is a string of
     recognized option letters; if a letter is followed by a colon, the
     option is expected to have an argument that may or may not be
     separated from it by white space.  optarg is set to point to the start
     of the option argument on return from getopt.
     getopt places in optind the argv index of the next argument to be
     processed.  The external variable optind is initialized to 1 before
     the first call to the function getopt.
     When all options have been processed (i.e., up to the first non-option
     argument), getopt returns EOF.  The special option -- can be used to
     delimit the end of the options; EOF is returned, and -- is skipped.
***************************************************************************/
#include <stdio.h>      /* For NULL, EOF */
#include <string.h>     /* For strchr() */
char    *optarg;        /* Global argument pointer. */
int     optind = 0;     /* Global argv index. */
static char     *scan = NULL;   /* Private scan pointer. */
int getopt( int argc, char * const argv[], const char* optstring)
{
   char c;
   char *posn;
   optarg = NULL;
   if (scan == NULL || *scan == '\0') {
       if (optind == 0)
           optind++;
       if (optind >= argc || argv[optind][0] != '-' || argv[optind][1] == '\0')
           return(EOF);
       if (strcmp(argv[optind], "--")==0) {
           optind++;
           return(EOF);
       }
       scan = argv[optind]+1;
       optind++;
   }
   c = *scan++;
   posn = strchr(optstring, c);        /* DDP */
   if (posn == NULL || c == ':') {
       fprintf(stderr, "%s: unknown option -%c\n", argv[0], c);
       return('?');
   }
   posn++;
   if (*posn == ':') {
       if (*scan != '\0') {
           optarg = scan;
           scan = NULL;
       } else {
           optarg = argv[optind];
           optind++;
       }
   }
   return(c);
}
