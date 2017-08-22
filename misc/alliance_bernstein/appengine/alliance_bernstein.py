#!/usr/bin/python

data = { '\xe4\xb8\xad\xe5\x9c\x8b\xe4\xb8\xbb\xe5\xb8\xad \xe7\xbf\x92\xe8\xbf\x91\xe5\xb9\xb3': { 'key': '\xe4\xb8\xad\xe5\x9c\x8b\xe4\xb8\xbb\xe5\xb8\xad \xe7\xbf\x92\xe8\xbf\x91\xe5\xb9\xb3',
                                                                                             '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                             '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                             '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                             '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                             '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '1',
                                                                                             '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                             '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '0',
                                                                                             '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0'},
  '\xe5\x8d\xb0\xe5\xba\xa6\xe7\xb8\xbd\xe7\x90\x86 \xe8\x8e\xab\xe8\xbf\xaa': { 'key': '\xe5\x8d\xb0\xe5\xba\xa6\xe7\xb8\xbd\xe7\x90\x86 \xe8\x8e\xab\xe8\xbf\xaa',
                                                                                 '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                 '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                 '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                 '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                 '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '1',
                                                                                 '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                 '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '0',
                                                                                 '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0'},
  '\xe6\x8a\x95\xe8\xb3\x87\xe5\xa4\xa7\xe5\xb8\xab \xe5\xb7\xb4\xe8\x8f\xb2\xe7\x89\xb9': { 'key': '\xe6\x8a\x95\xe8\xb3\x87\xe5\xa4\xa7\xe5\xb8\xab \xe5\xb7\xb4\xe8\x8f\xb2\xe7\x89\xb9',
                                                                                             '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                             '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                             '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                             '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                             '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '1',
                                                                                             '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                             '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '1',
                                                                                             '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1'},
  '\xe6\x97\xa5\xe6\x9c\xac\xe8\xbb\x9f\xe9\xab\x94\xe9\x8a\x80\xe8\xa1\x8c\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe5\xad\xab\xe6\xad\xa3\xe7\xbe\xa9': { 'key': '\xe6\x97\xa5\xe6\x9c\xac\xe8\xbb\x9f\xe9\xab\x94\xe9\x8a\x80\xe8\xa1\x8c\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe5\xad\xab\xe6\xad\xa3\xe7\xbe\xa9',
                                                                                                                                                         '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                                         '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                                                                                         '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                                         '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                                                                                         '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '0',
                                                                                                                                                         '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                                                                                         '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '0',
                                                                                                                                                         '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0'},
  '\xe7\x89\xb9\xe6\x96\xaf\xe6\x8b\x89\xe6\xb1\xbd\xe8\xbb\x8a\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe4\xbc\x8a\xe9\x9a\x86.\xe9\xa6\xac\xe6\x96\xaf\xe5\x85\x8b': { 'key': '\xe7\x89\xb9\xe6\x96\xaf\xe6\x8b\x89\xe6\xb1\xbd\xe8\xbb\x8a\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe4\xbc\x8a\xe9\x9a\x86.\xe9\xa6\xac\xe6\x96\xaf\xe5\x85\x8b',
                                                                                                                                                                      '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                                                      '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                                                                                                      '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                                                      '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                                                                                                      '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '0',
                                                                                                                                                                      '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                                                      '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '1',
                                                                                                                                                                      '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1'},
  '\xe7\xbe\x8e\xe5\x9c\x8b\xe7\xb8\xbd\xe7\xb5\xb1 \xe5\xb7\x9d\xe6\x99\xae': { 'key': '\xe7\xbe\x8e\xe5\x9c\x8b\xe7\xb8\xbd\xe7\xb5\xb1 \xe5\xb7\x9d\xe6\x99\xae',
                                                                                 '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                 '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                 '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                 '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                 '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '0',
                                                                                 '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                 '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '1',
                                                                                 '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1'},
  '\xe8\x87\x89\xe6\x9b\xb8\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe5\x85\x8b.\xe7\xa5\x96\xe5\x85\x8b\xe4\xbc\xaf': { 'key': '\xe8\x87\x89\xe6\x9b\xb8\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe5\x85\x8b.\xe7\xa5\x96\xe5\x85\x8b\xe4\xbc\xaf',
                                                                                                                                  '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                  '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                                                                  '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                  '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                                                                  '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '0',
                                                                                                                                  '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                                  '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '1',
                                                                                                                                  '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1'},
  '\xe8\x98\x8b\xe6\x9e\x9c\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe8\xb3\x88\xe4\xbc\xaf\xe6\x96\xaf': { 'key': '\xe8\x98\x8b\xe6\x9e\x9c\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe8\xb3\x88\xe4\xbc\xaf\xe6\x96\xaf',
                                                                                                         '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                         '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                                         '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                         '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '0',
                                                                                                         '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '0',
                                                                                                         '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                         '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '1',
                                                                                                         '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1'},
  '\xe9\x98\xbf\xe9\x87\x8c\xe5\xb7\xb4\xe5\xb7\xb4\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe9\x9b\xb2': { 'key': '\xe9\x98\xbf\xe9\x87\x8c\xe5\xb7\xb4\xe5\xb7\xb4\xe5\x89\xb5\xe8\xbe\xa6\xe4\xba\xba \xe9\xa6\xac\xe9\x9b\xb2',
                                                                                                                     '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                                                     '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                                                     '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                     '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                                                     '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '1',
                                                                                                                     '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                                     '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '0',
                                                                                                                     '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0'},
  '\xe9\xa6\x99\xe6\xb8\xaf\xe4\xbc\x81\xe6\xa5\xad\xe5\xae\xb6 \xe6\x9d\x8e\xe5\x98\x89\xe8\xaa\xa0': { 'key': '\xe9\xa6\x99\xe6\xb8\xaf\xe4\xbc\x81\xe6\xa5\xad\xe5\xae\xb6 \xe6\x9d\x8e\xe5\x98\x89\xe8\xaa\xa0',
                                                                                                         '\xe4\xba\x9e\xe6\xb4\xb2\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '1',
                                                                                                         '\xe5\x85\xa8\xe7\x90\x83\xe9\xab\x98\xe6\x94\xb6\xe7\x9b\x8a\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                                         '\xe5\x8d\xb0\xe5\xba\xa6\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                         '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\x82\xb5\xe5\x88\xb8': '1',
                                                                                                         '\xe6\x96\xb0\xe8\x88\x88\xe5\xb8\x82\xe5\xa0\xb4\xe5\xa4\x9a\xe5\x85\x83\xe8\xb3\x87\xe7\x94\xa2': '1',
                                                                                                         '\xe6\x97\xa5\xe6\x9c\xac\xe5\x83\xb9\xe5\x80\xbc\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0',
                                                                                                         '\xe7\xbe\x8e\xe5\x85\x83\xe8\xa4\x87\xe5\x90\x88\xe6\x94\xb6\xe7\x9b\x8a': '0',
                                                                                                         '\xe7\xbe\x8e\xe5\x9c\x8b\xe6\x88\x90\xe9\x95\xb7\xe5\x9e\x8b\xe8\x82\xa1\xe7\xa5\xa8': '0'}}
