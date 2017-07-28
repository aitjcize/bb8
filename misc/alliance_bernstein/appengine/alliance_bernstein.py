#!/usr/bin/python

data = { 'NBA\xe7\xb1\x83\xe7\x90\x83\xe5\x93\xa1 \xe6\x9e\x97\xe6\x9b\xb8\xe8\xb1\xaa': { 'key': 'NBA\xe7\xb1\x83\xe7\x90\x83\xe5\x93\xa1 \xe6\x9e\x97\xe6\x9b\xb8\xe8\xb1\xaa',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0.6',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                    '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0'},
  '\xe5\x8d\xb0\xe5\xba\xa6\xe7\xb8\xbd\xe7\x90\x86 \xe8\x8e\xab\xe8\xbf\xaa': { 'key': '\xe5\x8d\xb0\xe5\xba\xa6\xe7\xb8\xbd\xe7\x90\x86 \xe8\x8e\xab\xe8\xbf\xaa',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0.6',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.3',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.3',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0'},
  '\xe6\x8a\x95\xe8\xb3\x87\xe5\xa4\xa7\xe5\xb8\xab \xe5\xb7\xb4\xe8\x8f\xb2\xe7\x89\xb9': { 'key': '\xe6\x8a\x95\xe8\xb3\x87\xe5\xa4\xa7\xe5\xb8\xab \xe5\xb7\xb4\xe8\x8f\xb2\xe7\x89\xb9',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.5'},
  '\xe6\x97\xa5\xe6\x9c\xac\xe7\xb8\xbd\xe7\x90\x86 \xe5\xae\x89\xe5\x80\x8d\xe6\x99\x89\xe4\xb8\x89': { 'key': '\xe6\x97\xa5\xe6\x9c\xac\xe7\xb8\xbd\xe7\x90\x86 \xe5\xae\x89\xe5\x80\x8d\xe6\x99\x89\xe4\xb8\x89',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.1',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0'},
  '\xe6\xb3\x95\xe5\x9c\x8b\xe7\xb8\xbd\xe7\xb5\xb1 \xe9\xa6\xac\xe5\x85\x8b\xe5\xae\x8f': { 'key': '\xe6\xb3\x95\xe5\x9c\x8b\xe7\xb8\xbd\xe7\xb5\xb1 \xe9\xa6\xac\xe5\x85\x8b\xe5\xae\x8f',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                             '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0'},
  '\xe7\x89\xb9\xe6\x96\xaf\xe6\x8b\x89\xe6\xb1\xbd\xe8\xbb\x8a\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe4\xbc\x8a\xe9\x9a\x86.\xe9\xa6\xac\xe6\x96\xaf\xe5\x85\x8b': { 'key': '\xe7\x89\xb9\xe6\x96\xaf\xe6\x8b\x89\xe6\xb1\xbd\xe8\xbb\x8a\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe4\xbc\x8a\xe9\x9a\x86.\xe9\xa6\xac\xe6\x96\xaf\xe5\x85\x8b',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.1',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                                                                                                      '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.5'},
  '\xe7\xbe\x8e\xe5\x9c\x8b\xe7\xb8\xbd\xe7\xb5\xb1 \xe5\xb7\x9d\xe6\x99\xae': { 'key': '\xe7\xbe\x8e\xe5\x9c\x8b\xe7\xb8\xbd\xe7\xb5\xb1 \xe5\xb7\x9d\xe6\x99\xae',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.6',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.3',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                 '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '1'},
  '\xe8\x87\x89\xe6\x9b\xb8\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe5\x85\x8b.\xe7\xa5\x96\xe5\x85\x8b\xe4\xbc\xaf': { 'key': '\xe8\x87\x89\xe6\x9b\xb8\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe5\x85\x8b.\xe7\xa5\x96\xe5\x85\x8b\xe4\xbc\xaf',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                                                                  '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.5'},
  '\xe8\x98\x8b\xe6\x9e\x9c\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe8\xb3\x88\xe4\xbc\xaf\xe6\x96\xaf': { 'key': '\xe8\x98\x8b\xe6\x9e\x9c\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe8\xb3\x88\xe4\xbc\xaf\xe6\x96\xaf',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '0.3',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.1',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.5'},
  '\xe9\x98\xbf\xe9\x87\x8c\xe5\xb7\xb4\xe5\xb7\xb4\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe9\x9b\xb2': { 'key': '\xe9\x98\xbf\xe9\x87\x8c\xe5\xb7\xb4\xe5\xb7\xb4\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe9\x9b\xb2',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                                                     '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0'},
  '\xe9\xa6\x99\xe6\xb8\xaf\xe4\xbc\x81\xe6\xa5\xad\xe5\xae\xb6 \xe6\x9d\x8e\xe5\x98\x89\xe8\xaa\xa0': { 'key': '\xe9\xa6\x99\xe6\xb8\xaf\xe4\xbc\x81\xe6\xa5\xad\xe5\xae\xb6 \xe6\x9d\x8e\xe5\x98\x89\xe8\xaa\xa0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe4\xba\x9e\xe6\xb4\xb2\xe8\x82\xa1\xe7\xa5\xa8\xe5\x9f\xba\xe9\x87\x91': '1',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8\xe5\x9f\xba\xe9\x87\x91': '0.5',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0.3',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe6\x97\xa5\xe6\x9c\xac\xe7\xad\x96\xe7\x95\xa5\xe5\x83\xb9\xe5\x80\xbc\xe5\x9f\xba\xe9\x87\x91': '0',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9f\xba\xe9\x87\x91': '0.2',
                                                                                                         '\xe8\x81\xaf\xe5\x8d\x9a-\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x94\xb6\xe7\x9b\x8a\xe5\x9f\xba\xe9\x87\x91': '0'}}
