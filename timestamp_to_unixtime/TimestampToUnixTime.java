import java.text.SimpleDateFormat;

import org.apache.hadoop.hive.ql.exec.UDF;
import org.apache.hadoop.io.Text;

import java.util.Date;
import java.util.Locale;

public class TimestampToUnixTime extends UDF {
    public long evaluate(Text str) {
        if (str == null) {
            return -1;
        }

        try {
            SimpleDateFormat format = new SimpleDateFormat ("dd/MMM/yyyy:hh:mm:ss Z",  new Locale ("Locale.US"));
            Date date = format.parse(str.toString ().toLowerCase ());
            return date.getTime () / 1000;
        }
        catch (Throwable e) {
            e.printStackTrace ();
        }
        
        return -1;
    }
} 
