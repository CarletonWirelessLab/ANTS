/***************************************************************************
*  $Header: lanio.c 04/24/01
*  $Revision: 1.1 $
*  $Date: 10/24/01
*  PROGRAM NAME:   lanio.c
*
*  $Description:     Functions to talk to an Agilent signal generator
*                    via TCP/IP.  Uses command-line arguments.
*
*                    A TCP/IP connection to port 5025 is established and
*                    the resultant file descriptor is used to "talk" to the
*                    instrument using regular socket I/O mechanisms. $
*
*
*
*  Examples:
*
*   Query the signal generator frequency:
*        lanio xx.xxx.xx.x 'FREQ?'
*
*   Query the signal generator power level:
*        lanio xx.xxx.xx.x  'POW?'
*
*   Check for errors (gets one error):
*        lanio xx.xxx.xx.x  'syst:err?'
*
*   Send a list of commands from a file, and number them:
*        cat scpi_cmds | lanio -n xx.xxx.xx.x
*
****************************************************************************
*
*  This program compiles and runs under
*     - HP-UX 10.20 (UNIX), using HP cc or gcc:
*           + cc -Aa    -O -o lanio  lanio.c
*           + gcc -Wall -O -o lanio  lanio.c
*
*     - Windows 95, using Microsoft Visual C++ 4.0 Standard Edition
*     - Windows NT 3.51, using Microsoft Visual C++ 4.0
*           + Be sure to add  WSOCK32.LIB  to your list of libraries!
*           + Compile both lanio.c and getopt.c
*           + Consider re-naming the files to lanio.cpp and getopt.cpp
*
*  Considerations:
*     - On UNIX systems, file I/O can be used on network sockets.
*       This makes programming very convenient, since routines like
*       getc(), fgets(), fscanf() and fprintf() can be used.  These
*       routines typically use the lower level read() and write() calls.
*
*     - In the Windows environment, file operations such as read(), write(),
*       and close() cannot be assumed to work correctly when applied to
*       sockets.  Instead, the functions send() and recv() MUST be used.
*****************************************************************************/
/* Support both Win32 and HP-UX UNIX environment */
#ifdef _WIN32     /* Visual C++ 6.0 will define this */
#  define WINSOCK
#endif
#ifndef WINSOCK
#  ifndef _HPUX_SOURCE
#  define _HPUX_SOURCE
#  endif
#endif
#include <stdio.h>         /* for fprintf and NULL  */
#include <string.h>        /* for memcpy and memset */
#include <stdlib.h>        /* for malloc(), atol() */
#include <errno.h>         /* for strerror          */
#ifdef WINSOCK
#include <windows.h>
#  ifndef _WINSOCKAPI_
#  include <winsock.h>   // BSD-style socket functions
#  endif
#else                        /* UNIX with BSD sockets */
#  include <sys/socket.h>    /* for connect and socket*/
#  include <netinet/in.h>    /* for sockaddr_in       */
#  include <netdb.h>         /* for gethostbyname     */
#  define SOCKET_ERROR (-1)
#  define INVALID_SOCKET (-1)
   typedef  int SOCKET;
#endif /* WINSOCK */
#ifdef WINSOCK
  /* Declared in getopt.c.  See example programs disk. */
  extern char *optarg;
  extern int  optind;
  extern int getopt(int argc, char * const argv[], const char* optstring);
#else
#  include <unistd.h>           /* for getopt(3C) */
#endif
#define COMMAND_ERROR  (1)
#define NO_CMD_ERROR  (0)
#define SCPI_PORT  5025
#define INPUT_BUF_SIZE (64*1024)
/**************************************************************************
 * Display usage
 **************************************************************************/
static void usage(char *basename)
{
    fprintf(stderr,"Usage: %s [-nqu] <hostname> [<command>]\n", basename);
    fprintf(stderr,"       %s [-nqu] <hostname> < stdin\n", basename);
    fprintf(stderr,"  -n, number output lines\n");
    fprintf(stderr,"  -q, quiet; do NOT echo lines\n");
    fprintf(stderr,"  -e, show messages in error queue when done\n");
}

#ifdef WINSOCK
int init_winsock(void)
{
    WORD wVersionRequested;
    WSADATA wsaData;
    int err;
    wVersionRequested = MAKEWORD(1, 1);
    wVersionRequested = MAKEWORD(2, 0);
    err = WSAStartup(wVersionRequested, &wsaData);
    if (err != 0) {
        /* Tell the user that we couldn't find a useable */
        /* winsock.dll.     */
        fprintf(stderr, "Cannot initialize Winsock 1.1.\n");
        return -1;
    }
    return 0;
}

int close_winsock(void)
{
    WSACleanup();
    return 0;
}
#endif /* WINSOCK */
/***************************************************************************
 *
 > $Function: openSocket$
 *
 * $Description:  open a TCP/IP socket connection to the instrument $
 *
 * $Parameters:  $
 *    (const char *) hostname . . . . Network name of instrument.
 *                                    This can be in dotted decimal notation.
 *    (int) portNumber  . . . . . . . The TCP/IP port to talk to.
 *
 *
* $Return:     (int)  . . . . . . . . A file descriptor similar to open(1).$
*
* $Errors:     returns -1 if anything goes wrong $
*
***************************************************************************/
SOCKET openSocket(const char *hostname, int portNumber)
{
   struct hostent *hostPtr;
   struct sockaddr_in peeraddr_in;
   SOCKET s;
   memset(&peeraddr_in, 0, sizeof(struct sockaddr_in));
   /***********************************************/
   /* map the desired host name to internal form. */
   /***********************************************/
   hostPtr = gethostbyname(hostname);
   if (hostPtr == NULL)
   {
       fprintf(stderr,"unable to resolve hostname '%s'\n", hostname);
       return INVALID_SOCKET;
   }
   /*******************/
   /* create a socket */
   /*******************/
   s = socket(AF_INET, SOCK_STREAM, 0);
   if (s == INVALID_SOCKET)
   {
       fprintf(stderr,"unable to create socket to '%s': %s\n",
               hostname, strerror(errno));
       return INVALID_SOCKET;
   }
   memcpy(&peeraddr_in.sin_addr.s_addr, hostPtr->h_addr, hostPtr->h_length);
   peeraddr_in.sin_family = AF_INET;
   peeraddr_in.sin_port = htons((unsigned short)portNumber);
   if (connect(s, (const struct sockaddr*)&peeraddr_in,
               sizeof(struct sockaddr_in)) == SOCKET_ERROR)
               {
    fprintf(stderr,"unable to create socket to '%s': %s\n",
            hostname, strerror(errno));
    return INVALID_SOCKET;
   }
   return s;
}
/***************************************************************************
*
> $Function: commandInstrument$
*
* $Description:  send a SCPI command to the instrument.$
*
* $Parameters:  $
*     (FILE *) . . . . . . . . . file pointer associated with TCP/IP socket.
*     (const char *command)  . . SCPI command string.
* $Return:  (char *) . . . . . . a pointer to the result string.
*
* $Errors:   returns 0 if send fails $
*
***************************************************************************/
int commandInstrument(SOCKET sock,
                  const char *command)
  {
  int count;
/* fprintf(stderr, "Sending \"%s\".\n", command);  */
  if (strchr(command, '\n') == NULL) {
    fprintf(stderr, "Warning: missing newline on command %s.\n", command);
  }
  count = send(sock, command, strlen(command), 0);
  if (count == SOCKET_ERROR) {
    return COMMAND_ERROR;
  }
  return NO_CMD_ERROR;
}

/**************************************************************************
 * recv_line(): similar to fgets(), but uses recv()
 **************************************************************************/
char * recv_line(SOCKET sock, char * result, int maxLength)
{
  #ifdef WINSOCK
  int cur_length = 0;
  int count;
  char * ptr = result;
  int err = 1;
  while (cur_length < maxLength) {
      /* Get a byte into ptr */
      count = recv(sock, ptr, 1, 0);
      /* If no chars to read, stop. */
      if (count < 1) {
          break;
        }
      cur_length += count;
      /* If we hit a newline, stop. */
      if (*ptr == '\n') {
          ptr++;
          err = 0;
          break;
      }
      ptr++;
    }
    *ptr = '\0';
    if (err) {
      return NULL;
    } else {
        return result;
    }
#else
    /***********************************************************************

    * Simpler UNIX version, using file I/O.  recv() version works too.
* This demonstrates how to use file I/O on sockets, in UNIX.
***********************************************************************/
  FILE * instFile;
  instFile = fdopen(sock, "r+");
  if (instFile == NULL)
  {
    fprintf(stderr, "Unable to create FILE * structure : %s\n",
    strerror(errno));
    exit(2);
  }
  return fgets(result, maxLength, instFile);
#endif
}
/***************************************************************************
*
> $Function: queryInstrument$
*
* $Description:  send a SCPI command to the instrument, return a response.$
*
* $Parameters:  $
*     (FILE *) . . . . . . . . . file pointer associated with TCP/IP socket.
*     (const char *command)  . . SCPI command string.
*     (char *result) . . . . . . where to put the result.
*     (size_t) maxLength . . . . maximum size of result array in bytes.
*
* $Return:  (long) . . . . . . . The number of bytes in result buffer.
*
* $Errors:   returns 0 if anything goes wrong. $
*
***************************************************************************/
long queryInstrument(SOCKET sock,
                 const char *command, char *result, size_t maxLength)
                 {
                   long ch;
                   char tmp_buf[8];
                   long resultBytes = 0;
                   int command_err;
                   int count;

/*********************************************************
 * Send command to signal generator
 *********************************************************/
command_err = commandInstrument(sock, command);
if (command_err) return COMMAND_ERROR;
/*********************************************************
 * Read response from signal generator
 ********************************************************/
count = recv(sock, tmp_buf, 1, 0); /* read 1 char */
ch = tmp_buf[0];
if ((count < 1) || (ch == EOF)  || (ch == '\n'))
{
    *result = '\0';  /* null terminate result for ascii */
    return 0;
}
/* use a do-while so we can break out */
do
{
    if (ch == '#')
    {
        /* binary data encountered - figure out what it is */
        long numDigits;
        long numBytes = 0;
        /* char length[10]; */
        count = recv(sock, tmp_buf, 1, 0); /* read 1 char */
        ch = tmp_buf[0];
        if ((count < 1) || (ch == EOF)) break; /* End of file */
        if (ch < '0' || ch > '9') break;  /* unexpected char */
        numDigits = ch - '0';
        if (numDigits)
        {
            /* read numDigits bytes into result string. */
            count = recv(sock, result, (int)numDigits, 0);
            result[count] = 0;  /* null terminate */
            numBytes = atol(result);
        }
        if (numBytes)
        {
          resultBytes = 0;
          /* Loop until we get all the bytes we requested. */
          /* Each call seems to return up to 1457 bytes, on HP-UX 9.05 */
          do {
            int rcount;
            rcount = recv(sock, result, (int)numBytes, 0);
            resultBytes += rcount;
            result      += rcount;  /* Advance pointer */
          } while ( resultBytes < numBytes );
/************************************************************
 * For LAN dumps, there is always an extra trailing newline
 * Since there is no EOI line.  For ASCII dumps this is
 * great but for binary dumps, it is not needed.
 ***********************************************************/
          if (resultBytes == numBytes)
          {
            char junk;
            count = recv(sock, &junk, 1, 0);
          }
        }
        else
        {
          /* indefinite block ... dump til we can an extra line feed */
          do
          {
            if (recv_line(sock, result, maxLength) == NULL) break;
            if (strlen(result)==1 && *result == '\n') break;
            resultBytes += strlen(result);
            result += strlen(result);
          } while (1);
        }
      }
      else
      {
        /* ASCII response (not a binary block) */
        *result = (char)ch;

        if (recv_line(sock, result+1, maxLength-1) == NULL) return 0;
        /* REMOVE trailing newline, if present.  And terminate string. */
        resultBytes = strlen(result);
        if (result[resultBytes-1] == '\n') resultBytes -= 1;
        result[resultBytes] = '\0';
      }
    } while (0);
    return resultBytes;
  }
/*************************************************************************
*
> $Function: showErrors$
*
* $Description: Query the SCPI error queue, until empty.  Print results. $
*
* $Return:  (void)
*
*************************************************************************/
void showErrors(SOCKET sock)
{
  const char * command = "SYST:ERR?\n";
  char result_str[256];
  do
  {
    queryInstrument(sock, command, result_str, sizeof(result_str)-1);
/******************************************************************
* Typical result_str:
*     -221,"Settings conflict; Frequency span reduced."
*     +0,"No error"
* Don't bother decoding.
******************************************************************/
    if (strncmp(result_str, "+0,", 3) == 0) {
      /* Matched +0,"No error" */
      break;
    }

    puts(result_str);
  } while (1);
}
/***************************************************************************
*
> $Function: isQuery$
*
* $Description: Test current SCPI command to see if it a query. $
*
* $Return:  (unsigned char) . . . non-zero if command is a query.  0 if not.
*
***************************************************************************/
unsigned char isQuery( char* cmd )
{
  unsigned char q = 0 ;
  char *query ;
/*********************************************************/
/* if the command has a '?' in it, use queryInstrument.  */
/* otherwise, simply send the command.                   */
/* Actually, we must be a more specific so that   */
/* marker value querys are treated as commands.         */
/* Example:  SENS:FREQ:CENT (CALC1:MARK1:X?)             */
/*********************************************************/
  if ( (query = strchr(cmd,'?')) != NULL)
  {
/* Make sure we don't have a marker value query, or
 * any command with a '?' followed by a ')' character.
 * This kind of command is not a query from our point of view.
 * The signal generator does the query internally, and uses the result.
 */
    query++ ;       /* bump past '?' */
    while (*query)
    {
      if (*query == ' ') /* attempt to ignore white spc */
          query++ ;
      else break ;
    }

    if ( *query != ')' )
    {
      q = 1 ;
    }
  }
  return q ;
}
/***************************************************************************
*
> $Function: main$
*
* $Description: Read command line arguments, and talk to signal generator.
         Send query results to stdout. $
*
* $Return:  (int) . . . non-zero if an error occurs
*
***************************************************************************/
int main(int argc, char *argv[])
{
  SOCKET instSock;
  char *charBuf = (char *) malloc(INPUT_BUF_SIZE);
  char *basename;
  int chr;
  char command[1024];
  char *destination;
  unsigned char quiet = 0;
  unsigned char show_errs = 0;
  int number = 0;
  basename = strrchr(argv[0], '/');
  if (basename != NULL)
    basename++ ;
  else
    basename = argv[0];
  while ( ( chr = getopt(argc,argv,"qune")) != EOF )
    switch (chr)
    {
      case 'q':  quiet = 1; break;
      case 'n':  number = 1; break ;
      case 'e':  show_errs = 1; break ;
      case 'u':
      case '?':  usage(basename); exit(1) ;
    }
/* now look for hostname and optional <command>*/
  if (optind < argc)
  {
    destination = argv[optind++] ;
    strcpy(command, "");
    if (optind < argc)
    {
      while (optind < argc) {
    /* <hostname> <command> provided; only one command string */
      strcat(command, argv[optind++]);
      if (optind < argc) {
          strcat(command, " ");
        }
      else {
          strcat(command, "\n");
        }
      }
    }
    else
    {
      /*Only <hostname> provided; input on <stdin> */
      strcpy(command, "");
      if (optind > argc)
      {
        usage(basename);
        exit(1);
      }
    }
  }
  else
  {
    /* no hostname! */
    usage(basename);
    exit(1);
  }

/******************************************************
/* open a socket connection to the instrument
/******************************************************/
#ifdef WINSOCK
  if (init_winsock() != 0) {
      exit(1);
    }
#endif /* WINSOCK */
  instSock = openSocket(destination, SCPI_PORT);
  if (instSock == INVALID_SOCKET) {
      fprintf(stderr, "Unable to open socket.\n");
      return 1;
  }
  /* fprintf(stderr, "Socket opened.\n"); */
  if (strlen(command) > 0)
  {
/*******************************************************
/* if the command has a '?' in it, use queryInstrument. */
/* otherwise, simply send the command.                  */
/*******************************************************/
    if ( isQuery(command) )
    {
        long bufBytes;
        bufBytes = queryInstrument(instSock, command,
                                   charBuf, INPUT_BUF_SIZE);
        if (!quiet)
        {
            fwrite(charBuf, bufBytes, 1, stdout);
            fwrite("\n", 1, 1, stdout) ;
            fflush(stdout);
        }
    }
    else
    {
        commandInstrument(instSock, command);
    }
  }
  else
  {
    /* read a line from <stdin> */
    while ( gets(charBuf) != NULL )
    {
      if ( !strlen(charBuf) )
          continue ;
      if ( *charBuf == '#' || *charBuf == '!' )
          continue ;
      strcat(charBuf, "\n");
      if (!quiet)
      {
        if (number)
        {
          char num[10];
          sprintf(num,"%d: ",number);
          fwrite(num, strlen(num), 1, stdout);
        }
        fwrite(charBuf, strlen(charBuf), 1, stdout) ;
        fflush(stdout);
      }
      if ( isQuery(charBuf) )
      {
        long bufBytes;
        /* Put the query response into the same buffer as the*/
        /* command string appended after the null terminator.*/
        bufBytes = queryInstrument(instSock, charBuf,
                                   charBuf + strlen(charBuf) + 1,
                                   INPUT_BUF_SIZE -strlen(charBuf) );
        if (!quiet)
        {
            fwrite("  ", 2, 1, stdout) ;
            fwrite(charBuf + strlen(charBuf)+1, bufBytes, 1, stdout);
            fwrite("\n", 1, 1, stdout) ;
            fflush(stdout);
        }
      }
      else
      {
        commandInstrument(instSock, charBuf);
      }
      if (number) number++;
    }
  }
  if (show_errs) {
    showErrors(instSock);
  }
  #ifdef WINSOCK
    closesocket(instSock);
    close_winsock();
  #else
    close(instSock);
  #endif /* WINSOCK */
  return 0;
}
/* End of lanio.cpp  *
/**************************************************************************/
/* $Function: main1$                                                      */
/* $Description: Output a series of SCPI commands to the signal generator */
/*               Send query results to stdout. $                          */
/*                                                                        */
/* $Return:  (int) . . . non-zero if an error occurs                      */
/*                                                                        */
/**************************************************************************/
/* Rename this int main1() function to int main(). Re-compile and the     */
/* execute the program                                                    */
/**************************************************************************/
int main1()
{
  SOCKET instSock;
  long bufBytes;

  char *charBuf = (char *) malloc(INPUT_BUF_SIZE);
/*********************************************/
/* open a socket connection to the instrument*/
/*********************************************/
  #ifdef WINSOCK
    if (init_winsock() != 0) {
    exit(1);
    }
  #endif /* WINSOCK */
  instSock = openSocket("xxxxx", SCPI_PORT); /* Put your hostname here */
  if (instSock == INVALID_SOCKET) {
    fprintf(stderr, "Unable to open socket.\n");
    return 1;
  }
  /* fprintf(stderr, "Socket opened.\n"); */
  bufBytes = queryInstrument(instSock, "*IDN?\n", charBuf, INPUT_BUF_SIZE);
  printf("ID: %s\n",charBuf);
  commandInstrument(instSock, "FREQ 2.5 GHz\n");
  printf("\n");
  bufBytes = queryInstrument(instSock, "FREQ:CW?\n", charBuf, INPUT_BUF_SIZE);
  printf("Frequency: %s\n",charBuf);
  commandInstrument(instSock, "POW:AMPL -5 dBm\n");
  bufBytes = queryInstrument(instSock, "POW:AMPL?\n", charBuf, INPUT_BUF_SIZE);
  printf("Power Level: %s\n",charBuf);
  printf("\n");
  #ifdef WINSOCK
    closesocket(instSock);
    close_winsock();
  #else
    close(instSock);
  #endif /* WINSOCK */
  return 0;
}
