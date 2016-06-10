#!/bin/sh
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Try to add team fields to deliverable files that don't have them.

list-deliverables | while read team deliverable; do
    for filename in deliverables/*/${deliverable}.yaml; do
        if [ -f $filename ]; then
            if grep -q '^team:' $filename; then
                continue
            fi
            echo $filename
            sed -i "/^launchpad:/a team: $team" $filename
        fi
    done
done
