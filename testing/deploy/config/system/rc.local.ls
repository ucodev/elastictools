# Start logstash
export LS_HEAP_SIZE="2g"
/bin/su logstash -- /opt/elk-solution/logstash/bin/logstash -f /opt/elk-solution/config/logstash-indexer.conf &

# Redirect ports
/sbin/iptables -t nat -A PREROUTING -p udp --dport 514 -j REDIRECT --to-port 5000
/sbin/iptables -t nat -A PREROUTING -p tcp --dport 514 -j REDIRECT --to-port 5000

