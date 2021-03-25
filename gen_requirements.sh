pipreqs --ignore bci_framework/default_projects,bci_framework/documentation,bci_framework/extensions/stimuli_delivery/path,bci_framework/kafka_scripts/latency_synchronization_stimuli_marker --savepath requirements.tmp --force bci_framework
rm requirements.txt
sed '/kafka==/d' requirements.tmp >> requirements.txt
rm requirements.tmp
cat requirements.txt