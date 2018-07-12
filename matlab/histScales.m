function [] = histScales(fig, data, ybar, gtitle, xlab, xstep, xlimits)


h = figure(fig);
close(h);
h = figure(fig);


if isempty(xlimits)
    x1 = floor(min(data)); 
    x2 = ceil(max(data));
else
    x1 = xlimits(1);
    x2 = xlimits(2);
end
    
if ybar

    y = ybar;
    sp = subplot(5,1,1:2);
    hist(data,x1:xstep:x2);
    title(gtitle);
    axis([x1 x2 y inf])
    set(sp,'XTick',zeros(1,0));
    
    subplot(5,1,3:5);
    hist(data,x1:xstep:x2);
    xlabel(xlab)
    axis([x1 x2 0 y])
else
    hist (data,x1:xstep:x2)
    title(gtitle);
    xlabel(xlab);
    xlim([x1 x2])
end