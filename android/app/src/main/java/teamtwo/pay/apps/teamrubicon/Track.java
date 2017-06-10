package teamtwo.pay.apps.teamrubicon;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;

/**
 * Created by kenneth on 6/10/17.
 */

public class Track extends AppCompatActivity {

    Button btnStopTrack, btnEmergency;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tracking);

        btnStopTrack = (Button) findViewById(R.id.btnStopTracking);
        btnStopTrack.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                //Close the users session
                SharedPreferences pref = getSharedPreferences("MyPref", 1); // 0 - for private mode
                SharedPreferences.Editor editor = pref.edit();
                editor.remove("email");
                editor.commit();

                //Stop GPS service
                //Initialize GPS tracking
                Intent intent = new Intent(getApplicationContext(), GPSService.class);
                stopService(intent);

                Intent main = new Intent(getBaseContext(), MainActivity.class);
                startActivity(main);
                finish();
            }
        });
    }
}
