function [test_output] = get_current_time()

    test_output = datetime('now');
    disp('Matlab will now pause for 5 seconds');
    pause(5);
    disp('Done with current time\n');

end