# Verified MAXs/Paragon-compatible command subset

| Command | Verified meaning | ODS relation |
|---:|---|---|
| 1 | Write string | `terminal.write` |
| 6 | Read bounded line | `terminal.read_line` |
| 8 | Read key and origin | `terminal.read_key` |
| 9 | Disconnect/twit user | `lifecycle.disconnect` |
| 10 | Display text file | outside ODS Core 0.1 |
| 11 | Check file availability | outside ODS Core 0.1 |
| 13 | Read integer user information | `session.identity` (partial) |
| 14 | Read user/BBS string information | `session.identity` (partial) |
| 20 | Normal door shutdown | `lifecycle.exit` |

The source also permits arbitrary menu-function numbers through the message command field. ODS models that as `bbs.command`; it does not claim every numeric command has been identified.
