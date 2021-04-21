rm requirements.txt
pipreqs --ignore bci_framework/default_projects,bci_framework/documentation,bci_framework/extensions/stimuli_delivery/path,bci_framework/kafka_scripts/latency_synchronization_stimuli_marker --savepath requirements.txt --force bci_framework
sed -i '/kafka==/d' requirements.txt
sed -i '/browser==/d' requirements.txt
sed -i '/seaborn==/d' requirements.txt
sed -i 's/==.*//' requirements.txt
python -c "[print(f'\'{line[:-1]}\',') for line in open('requirements.txt').readlines()]"
