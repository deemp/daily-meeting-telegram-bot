import { createMachine, assign } from 'xstate';

export const machine = createMachine({
    /** @xstate-layout N4IgpgJg5mDOIC5SzAFwPoFsxoJYDspZ1VdsAvAe3zADoBVFAJwEkIAbMAYhVUbCYAVMmCo0A2gAYAuolAAHSrFylqckAA9EAJgDMAdgCMtbQA5dp0wFZthgCwA2bXf0AaEAE9Eh-Q9qSAyQcrA11DQ1NtbQBfaPdeLBxSQmJSCmo6ACFKVFoACQBDfA4wAGFKTEwiiFpSgAswAGMAaxZ8ADNKAEEAI0oAVz5mLilZJBBFZVV8dS0EXW19WgBOXysHZYc7KyNdZbt3LwQ7SSt-QwDtZYNTO1XdWPi0RLwUkhExLJz86s5yyuqtQaLTanV6AyGAhGhjGCiUKlwanGcwWS1WwQ2Wx2hj2B08iAcujsKwcpn0IX0klsy1My0eIAS2FeRHe6RotGyuUKxT+FSqxQYzEKsAAUpQCJAALJJAhEEYydSTBFI0BzcxnXy6STkwx6Kz67SHRB7Uy0KzLKyScwXMJ2cL0xkyt5pUQZDnfbklf78mr8JjCsUSiDS5mwaGwibw6azRDq2ia7VWXW6fU2I0IJMavT3E6kk4POIM55M5Isl2fd1c35lPmAv3CwSUQP4EOl2AAMVwTFgqC4Gh7BVQdAK7SHTAAFJbJABKHjFp1lj5uzk-Hk1gEC+sFWCN5ut2Udrs90aKqOImbI7wOQkrfTLC7LZanWw49OmQzLWha2zWdYWyS6AWTwYCWB6sq67Irp6vIbjUADKaB+sIbLcP2qCDsOo4CJOASzo6obgRWUHVt6gIIZCQhLhICrjEq0aXgghjXrot73pIj7PuEujpnsSzWFcdhXBsth7A684EeWy4eiRtabkK26NqUTBgBhAAKTC4AAbhh9SDgA6iodScn2A5DrQI5jjhM5ziBC6pFRXxVmupFyQIDaUEpKlDupWk6XU+mGZyJ60WeKqaFe+gsasbEcTYXHpvo+jaLQdzkoJZLarSMSFvhbaEW6qn9D07C4I0um5MhEE1h0XZVNMJnoWZFnYVOeHiXlknsoVxWleVtCVZ85Q1UwdXnsFcJTOeMYZoa+IIO+X5RMs2hJrsBqmGJtkSQ5tDdSVZX+RVDnkUN7S1YO54NRh5lYROrU2S8HU7XtvWHf1x1oKd53TONkaTWFcx6EYJjmJYcWOM4bhzcEn4Wh+16PhYdqGJtj1gZ1dAvQdg60HuC7qRU8i9mh13NXduEPaBzrPUV+19XjzIE5gRO-XRU0MUDxhmBY-H2E4LhvuSJirJIEQ2Pqdwozl7XozTPXY7kPnaUO5VM0TV1NbdVltVtT0obttOvTjSt+YOauoKzoUXqqOgGFzoO8xDAtzYlyWpVY6WUvotIFoW+CUBAcDqLlssoae-3W+FCAALRROm0dnI+SfJ8nSWo1Ti7636bCcOHyqR4D6zGIYFIOEEDj2NqeJHNeidWLcWwXBsXHp3Z+WQTkef0TbCDaA46ZMSxUQhABmw6o+2XAWj1P68RzmyRAXfsz3+jVzolpmnYkRXDilg6vorfbbP0nz7BQJNK0HTdH0gx+kvAPeHHc0nJ+RIATsQS6KSG3S7rodVZWVcXoF6CjctuZsUo7L3wLogc0xgALUhxIsSkVh0wnGSstCkPgHDe3rgfX+09M4ALnsAs+W4dxNnFC2OynZuyoGgdNHYyUghJgWHsdYq9ljpkJMlSwL8y73nWJIOwh89bEJPqQn0tByJIQcgwhi4RRYrCTiEFaPMK48QMLQMk4QPZhCpFqbYoj-5EQkTBKR5DFLKTUhpZWZRDoGVQEZTuIUI7TXCJEM0iwwhGDsIY6w6ZWG0EJNcVeCxm72GMTPABWNyryJ7j4TYX5hFJWsDwmkpgeIBFoLqXwkRNR5nwVPDO9l9axLeupMAmlET9FgNKWAsACgwHgK4-O7iJ7CyuMtVYW99jcTmhYJY2wgjamuJaPYdICElPbpjQ2Ct3ooS+iNC6YU2YP0YrcYkhjUnrAWBktB2wVjoN-Do3wRSix-2iRWcpOMBoZBOtQM6yzu5-TaQozZySXBmF2VcSw3C+7xitMMq4X8tRS2KW3DGBt5b0yofuQg5t4lRzFmccJpgYbWEpIJN8SZ4yPjLtoFJNhCRRKIdcuZfUTYq0Ooi1pLy5gRBvOsFadg-FPnMCtBKdx-ABF1CExYzFYixCAA */
  id: "set_meetings_timezone",
  initial: "UserIdle",
  context: {
    userTimezone: null,
    meetingTime: '2024-06-30T10:00:00Z', // base meeting time in UTC
  },
  states: {
    UserIdle: {
      on: {
        setUserTimezone: {
          actions: 'setUserTimezone',
          target: "PublicChat.TimezoneConfirmation"
        }
      }
    },
    Bot: {
      states: {
        HandleCommand: {
          initial: "CheckInfoAboutUser",
          states: {
            CheckInfoAboutUser: {
              always: [
                {
                  target: "UserHasJoinedMeetings",
                  cond: "userHasJoinedMeetings"
                },
                {
                  target: "UserHasToJoinMeetingsFirst",
                }
              ]
            },
            UserHasJoinedMeetings: {
              always: [
                {
                  target: "SetUserTimezone",
                  cond: "userHasPrivateChatWithBot"
                },
                {
                  target: "UserHasToCreatePrivateChatWithBot",
                }
              ]
            },
            UserHasToJoinMeetingsFirst: {
              after: {
                500: {
                  target: "#set_meetings_timezone.PublicChat.JoinMeetingPrompt",
                }
              }
            },
            SetUserTimezone: {
              entry: 'setUserTimezone',
              after: {
                500: {
                  target: "#set_meetings_timezone.PublicChat.TimezoneSetConfirmation",
                }
              },
              description: "- Set timezone for this User and save in the bot.\n- Update scheduled reminders for daily meetings if the User participates in them"
            },
            UserHasToCreatePrivateChatWithBot: {
              after: {
                500: {
                  target: "#set_meetings_timezone.PublicChat.PrivateChatPrompt",
                }
              }
            }
          }
        }
      }
    },
    PublicChat: {
      initial: "PreviousMessages",
      states: {
        PreviousMessages: {},
        TimezoneConfirmation: {
          description: "/set_meetings_timezone <current time or timezone> - <current time or timezone> - the user's current time, rely on this time bot will suggest your timezone. usage example: /set_meetings_timezone 13:20 or /set_meetings_timezone Europe/Moscow the output will inline buttons with suggestions",
          after: {
            500: {
              target: "#set_meetings_timezone.Bot.HandleCommand",
            }
          }
        },
        TimezoneSetConfirmation: {
          description: "Reply: \"Time zone is successfully set to <Europe/Moscow> (<any region>)>\"",
          after: {
            500: {
              target: "#set_meetings_timezone.UserIdle",
            }
          }
        },
        JoinMeetingPrompt: {
          description: "Reply: \"You have to join daily meetings first! Use the /join command.\"",
          after: {
            500: {
              target: "#set_meetings_timezone.UserIdle",
            }
          }
        },
        PrivateChatPrompt: {
          description: "Reply: \"You should first create a Private chat with <bot> (it's me).\"",
          after: {
            500: {
              target: "#set_meetings_timezone.UserIdle",
            }
          }
        }
      }
    }
  }
});
   
